"""
story_service — 상인 스토리 자동 생성

POST /api/v1/merchant/stories

흐름:
  1. store_id → Store + Products 로드
  2. LLM(Anthropic Claude) 호출 → 스토리 문구 생성
  3. AI 실패 시 fallback 템플릿 반환
  4. 생성된 스토리를 Store.store_story_summary에 선택적 저장

환경변수:
  ANTHROPIC_API_KEY : Claude API 키 (없으면 fallback)
"""
import logging
import re
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.store import Store
from app.db.models.product import Product
from app.db.models.merchant import Merchant
from app.core.config import settings

logger = logging.getLogger(__name__)


def _candidate_story_models() -> list[str]:
    preferred = (settings.ANTHROPIC_MODEL_STORY or "").strip()
    models = [
        preferred,
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-haiku-20240307",
    ]
    return [m for i, m in enumerate(models) if m and m not in models[:i]]


# ──────────────────────────────────────────────
# Fallback 템플릿
# ──────────────────────────────────────────────

_FALLBACK_TEMPLATES = [
    "{store_name}에 오신 것을 환영합니다! 오늘도 신선한 제품을 준비했습니다.",
    "{store_name}의 {product_list}을(를) 만나보세요. 정성껏 준비한 상품입니다.",
    "전통시장의 맛과 정성, {store_name}에서 직접 경험해 보세요.",
]


def _fallback_story(store_name: str, product_names: list[str]) -> str:
    product_list = ", ".join(product_names[:3]) if product_names else "다양한 상품"
    template = _FALLBACK_TEMPLATES[len(product_names) % len(_FALLBACK_TEMPLATES)]
    return template.format(store_name=store_name, product_list=product_list)


def _mask_sensitive(text: str) -> str:
    masked = text
    masked = re.sub(r'([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})', '[이메일]', masked)
    masked = re.sub(r'01[016789]-?\d{3,4}-?\d{4}', '[전화번호]', masked)
    masked = re.sub(r'\d{6}-?\d{7}', '[주민번호]', masked)
    return masked


def _tone_prefix(tone: str) -> str:
    if tone == "전문적인":
        return "신뢰할 수 있는 품질 기준과 정확한 안내를 바탕으로"
    if tone == "정겨운":
        return "시장 이웃처럼 따뜻한 마음으로"
    return "친근하고 알기 쉬운 설명으로"


def _clean_story_text(text: str) -> str:
    """LLM 출력에서 마크다운/중복/불필요 개행 제거."""
    s = (text or "").strip()
    s = re.sub(r"[#*_`>{}\[\]\|]", " ", s)   # markdown-ish chars
    s = re.sub(r"^(스토리|결과|출력)\s*[:：]\s*", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    # 같은 문장 반복 제거
    sentences = re.split(r"(?<=[.!?])\s+|(?<=다\.)\s+", s)
    uniq = []
    seen = set()
    for sent in sentences:
        t = sent.strip()
        if not t:
            continue
        key = re.sub(r"\s+", "", t)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(t)
    out = " ".join(uniq).strip()
    out = re.sub(r"\s{2,}", " ", out)
    return out


def _split_korean_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=다\.)\s+|(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _build_story_versions(base_story: str, tone: str, interview_text: str) -> dict:
    intro = _tone_prefix(tone)
    cleaned = _clean_story_text(base_story)
    _ = _clean_story_text(interview_text.strip())

    sentences = _split_korean_sentences(cleaned)
    if not sentences:
        sentences = [cleaned] if cleaned else []

    core_1 = " ".join(sentences[:1]).strip()
    core_2 = " ".join(sentences[:2]).strip() if len(sentences) >= 2 else core_1
    core_3 = " ".join(sentences[:3]).strip() if len(sentences) >= 3 else core_2

    short = f"{intro} {core_1}".strip()
    normal = f"{intro} {core_2}".strip()
    detailed = f"{intro} {core_3}".strip()

    return {"short": short, "normal": normal, "detailed": detailed}


def _normalize_tag(raw: str) -> str:
    t = re.sub(r"[^0-9A-Za-z가-힣]", "", raw or "")
    t = re.sub(r"(kg|g|ml|l|팩|봉|개|단|마리|손)$", "", t, flags=re.IGNORECASE)
    return t[:12]


def _extract_topic_words(text: str) -> list[str]:
    candidates = re.findall(r"[가-힣A-Za-z]{2,12}", text or "")
    stop = {
        "오늘", "이번", "저희", "우리", "정말", "그냥", "추천", "설명", "소개", "문구",
        "손님", "고객", "시장", "점포", "상점", "입니다", "합니다", "그리고", "하지만",
    }
    words: list[str] = []
    for c in candidates:
        n = _normalize_tag(c)
        if len(n) < 2 or n in stop:
            continue
        words.append(n)
    return words


def _build_hashtags(
    keywords: Optional[list[str]],
    product_names: list[str],
    interview_text: str,
    story_text: str,
) -> list[str]:
    tags: list[str] = []
    if keywords:
        for kw in keywords[:4]:
            norm = _normalize_tag(kw.strip())
            if norm:
                tags.append(f"#{norm}")
    for p in product_names[:3]:
        norm = _normalize_tag(p.strip())
        if norm:
            tags.append(f"#{norm}")
    for w in _extract_topic_words(f"{interview_text} {story_text}")[:4]:
        tags.append(f"#{w}")
    # 중복 제거
    unique = []
    seen = set()
    for tag in tags:
        if tag not in seen:
            unique.append(tag)
            seen.add(tag)
    return unique[:5]


def _resolve_store_id(db: Session, user, requested_store_id: Optional[str]) -> str:
    if requested_store_id:
        return requested_store_id

    row = (
        db.query(Merchant.store_id)
        .filter(Merchant.user_id == user.user_id)
        .order_by(Merchant.created_at.asc())
        .first()
    )
    if row and row[0]:
        return row[0]

    # 시연 환경 보정: 매핑 누락 시 첫 점포로 fallback
    demo_store = (
        db.query(Store.store_id)
        .order_by(Store.created_at.asc())
        .first()
    )
    if demo_store and demo_store[0]:
        logger.warning("merchant-store 매핑 누락, demo store fallback 사용: user_id=%s", getattr(user, "user_id", "unknown"))
        return demo_store[0]

    raise HTTPException(status_code=404, detail="상인 계정에 연결된 점포가 없습니다.")


# ──────────────────────────────────────────────
# LLM 호출 (Anthropic Claude)
# ──────────────────────────────────────────────

def _call_llm(
    store_name: str,
    store_desc: Optional[str],
    product_names: list[str],
    interview_text: str,
    keywords: Optional[list[str]],
) -> str:
    """
    Claude API 호출.
    실패 시 Exception raise → 호출 측에서 fallback 처리.
    """
    api_key = (settings.ANTHROPIC_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 미설정")

    try:
        import anthropic  # type: ignore
    except ImportError:
        raise RuntimeError("anthropic 패키지가 설치되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)

    product_str = ", ".join(product_names[:5]) if product_names else "미지정"
    desc_str = f"점포 소개: {store_desc}\n" if store_desc else ""
    keyword_str = ", ".join((keywords or [])[:5]) if keywords else "미지정"
    interview_str = interview_text.strip() if interview_text.strip() else "미지정"

    prompt = (
        f"당신은 전통시장 상인의 스토리 작가입니다.\n"
        f"다음 정보를 바탕으로 고객의 마음을 끄는 따뜻한 스토리 문구를 2~3문장으로 작성하세요.\n"
        f"규칙: 마크다운(#, **, -, 목록) 금지 / 문장 반복 금지 / 제공된 점포·상품 맥락에서 벗어나지 말 것.\n\n"
        f"점포명: {store_name}\n"
        f"{desc_str}"
        f"상인 소개문(핵심): {interview_str}\n"
        f"키워드: {keyword_str}\n"
        f"주요 판매 상품: {product_str}\n\n"
        f"스토리 문구 (2~3문장, 한국어, 평문만):"
    )

    last_error: Optional[Exception] = None
    for model_name in _candidate_story_models():
        try:
            message = client.messages.create(
                model=model_name,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"지원 가능한 Anthropic 모델을 찾지 못했습니다: {last_error}")


# ──────────────────────────────────────────────
# 서비스 메인
# ──────────────────────────────────────────────

def generate_story(
    db: Session,
    user,
    store_id: Optional[str],
    save_to_store: bool = False,
    interview_text: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    tone: str = "친근한",
    selected_length: str = "normal",
    llm_fn=None,           # 테스트용 DI
) -> dict:
    """
    상인 스토리 생성.
    - merchant 권한 검증
    - Store + Product 로드
    - LLM 호출 (실패 시 fallback)
    - save_to_store=True면 Store.store_story_summary 업데이트
    """
    if user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="상인 권한이 필요합니다.")

    resolved_store_id: Optional[str] = None
    store: Optional[Store] = None
    product_names: list[str] = []

    try:
        resolved_store_id = _resolve_store_id(db, user, store_id)
    except HTTPException:
        # 시연 정책: 점포 매핑이 없어도 입력 기반 스토리 생성 허용
        resolved_store_id = None

    if resolved_store_id:
        store = db.query(Store).filter(Store.store_id == resolved_store_id).first()

    if store:
        products = (
            db.query(Product)
            .filter(Product.store_id == resolved_store_id)
            .order_by(Product.created_at.desc())
            .limit(10)
            .all()
        )
        product_names = [p.product_name for p in products]
        store_name = store.store_name
        store_desc = getattr(store, "store_story_summary", None)
    else:
        # 점포 미매핑 상태에서도 입력 기반으로 생성 가능하게 가상 컨텍스트 사용
        store_name = f"{getattr(user, 'name', '상인')}님의 점포"
        store_desc = None
        resolved_store_id = "virtual-store"

    fallback_mode = False
    story_text = ""
    masked_interview = _mask_sensitive(interview_text or "")

    if llm_fn is not None:
        # 테스트용 주입
        try:
            story_text = llm_fn(
                store_name=store_name,
                store_desc=store_desc,
                product_names=product_names,
            )
        except Exception as e:
            logger.warning("LLM(테스트 주입) 실패: %s", e)
            story_text    = _fallback_story(store_name, product_names)
            fallback_mode = True
    else:
        try:
            story_text = _call_llm(
                store_name=store_name,
                store_desc=store_desc,
                product_names=product_names,
                interview_text=masked_interview,
                keywords=keywords,
            )
        except Exception as e:
            logger.warning("LLM 호출 실패 — fallback: %s", e)
            story_text    = _fallback_story(store_name, product_names)
            fallback_mode = True

    story_versions = _build_story_versions(story_text, tone, masked_interview)
    if selected_length not in story_versions:
        selected_length = "normal"
    selected_story = story_versions[selected_length]
    hashtags = _build_hashtags(
        keywords=keywords,
        product_names=product_names,
        interview_text=masked_interview,
        story_text=selected_story,
    )

    if save_to_store and not fallback_mode and store:
        store.store_story_summary = selected_story
        db.commit()

    return {
        "store_id": resolved_store_id,
        "store_name": store_name,
        "story": selected_story,
        "story_versions": story_versions,
        "selected_length": selected_length,
        "tone": tone,
        "hashtags": hashtags,
        "interview_masked": masked_interview,
        "fallback_mode": fallback_mode,
        "products_used": product_names[:5],
    }
