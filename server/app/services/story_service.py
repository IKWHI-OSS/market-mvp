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
import os
import logging
import re
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.store import Store
from app.db.models.product import Product

logger = logging.getLogger(__name__)


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


def _build_story_versions(base_story: str, tone: str, interview_text: str) -> dict:
    intro = _tone_prefix(tone)
    interview_line = interview_text.strip()
    short = f"{intro} {base_story}".strip()
    if len(short) > 80:
        short = short[:77].rstrip() + "..."
    normal = short
    detailed = short
    if interview_line:
        normal = f"{short}\n{interview_line}"
        detailed = f"{short}\n{interview_line}\n오늘도 제철 재료와 점포만의 기준으로 장보기 경험을 더 좋게 만들겠습니다."
    return {
        "short": short,
        "normal": normal,
        "detailed": detailed,
    }


def _build_hashtags(keywords: Optional[list[str]], product_names: list[str]) -> list[str]:
    tags: list[str] = []
    if keywords:
        for kw in keywords[:3]:
            norm = kw.strip().replace(" ", "")
            if norm:
                tags.append(f"#{norm}")
    for p in product_names[:2]:
        norm = p.strip().replace(" ", "")
        if norm:
            tags.append(f"#{norm}")
    # 중복 제거
    unique = []
    seen = set()
    for tag in tags:
        if tag not in seen:
            unique.append(tag)
            seen.add(tag)
    return unique


# ──────────────────────────────────────────────
# LLM 호출 (Anthropic Claude)
# ──────────────────────────────────────────────

def _call_llm(store_name: str, store_desc: Optional[str], product_names: list[str]) -> str:
    """
    Claude API 호출.
    실패 시 Exception raise → 호출 측에서 fallback 처리.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 미설정")

    try:
        import anthropic  # type: ignore
    except ImportError:
        raise RuntimeError("anthropic 패키지가 설치되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)

    product_str = ", ".join(product_names[:5]) if product_names else "다양한 상품"
    desc_str    = f"점포 소개: {store_desc}\n" if store_desc else ""

    prompt = (
        f"당신은 전통시장 상인의 스토리 작가입니다.\n"
        f"다음 정보를 바탕으로 고객의 마음을 끄는 따뜻한 스토리 문구를 2~3문장으로 작성하세요.\n\n"
        f"점포명: {store_name}\n"
        f"{desc_str}"
        f"주요 판매 상품: {product_str}\n\n"
        f"스토리 문구 (2~3문장, 한국어):"
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ──────────────────────────────────────────────
# 서비스 메인
# ──────────────────────────────────────────────

def generate_story(
    db: Session,
    user,
    store_id: str,
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

    store: Optional[Store] = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="점포를 찾을 수 없습니다.")

    products = (
        db.query(Product)
        .filter(Product.store_id == store_id)
        .order_by(Product.created_at.desc())
        .limit(10)
        .all()
    )
    product_names = [p.product_name for p in products]
    store_name    = store.store_name
    store_desc    = getattr(store, "store_story_summary", None)

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
            story_text = _call_llm(store_name, store_desc, product_names)
        except Exception as e:
            logger.warning("LLM 호출 실패 — fallback: %s", e)
            story_text    = _fallback_story(store_name, product_names)
            fallback_mode = True

    story_versions = _build_story_versions(story_text, tone, masked_interview)
    if selected_length not in story_versions:
        selected_length = "normal"
    selected_story = story_versions[selected_length]
    hashtags = _build_hashtags(keywords, product_names)

    if save_to_store and not fallback_mode:
        store.store_story_summary = selected_story
        db.commit()

    return {
        "store_id": store_id,
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
