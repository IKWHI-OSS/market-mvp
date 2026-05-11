"""
price_service — KAMIS 농산물 시세 연동 및 Product 가격 자동 업데이트

KAMIS Open API v2 (https://www.kamis.or.kr)
  - 인증키가 없거나 외부 호출 실패 시 fallback 데이터로 대체한다.

환경변수:
  KAMIS_API_KEY   : KAMIS 인증키
  KAMIS_API_ID    : KAMIS 신청자 ID (기본 "test")
"""
import os
import uuid
import logging
from datetime import date, datetime
from typing import Optional

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.market_price import PriceChangeReasonEnum
from app.db.models.product import Product
from app.db.repositories import price_repository as repo

logger = logging.getLogger(__name__)

KAMIS_BASE_URL = "https://www.kamis.or.kr/service/price/xml.do"

# 품목코드 매핑 — 30품목 (채소 8 / 과일 8 / 수산물 7 / 육류 7)
# 코드/이름은 scripts/generate_mock_v2.py 의 KAMIS_ITEMS 와 동기화되어 있음.
KAMIS_ITEM_MAP: dict[str, dict] = {
    # 채소
    "112": {"item_name": "배추/포기",     "unit": "1포기", "category": "채소"},
    "151": {"item_name": "무/일반",       "unit": "1개",   "category": "채소"},
    "152": {"item_name": "당근",          "unit": "1kg",   "category": "채소"},
    "153": {"item_name": "양파",          "unit": "1.5kg", "category": "채소"},
    "154": {"item_name": "대파",          "unit": "1단",   "category": "채소"},
    "155": {"item_name": "마늘/깐마늘",   "unit": "1kg",   "category": "채소"},
    "156": {"item_name": "청양고추",      "unit": "100g",  "category": "채소"},
    "157": {"item_name": "시금치",        "unit": "200g",  "category": "채소"},
    # 과일
    "214": {"item_name": "사과/후지",     "unit": "10개",  "category": "과일"},
    "215": {"item_name": "배/신고",       "unit": "10개",  "category": "과일"},
    "216": {"item_name": "감귤/제주",     "unit": "3kg",   "category": "과일"},
    "217": {"item_name": "샤인머스캣",    "unit": "500g",  "category": "과일"},
    "218": {"item_name": "딸기/설향",     "unit": "500g",  "category": "과일"},
    "219": {"item_name": "수박/일반",     "unit": "1통",   "category": "과일"},
    "421": {"item_name": "감/단감",       "unit": "10개",  "category": "과일"},
    "422": {"item_name": "복숭아/백도",   "unit": "5개",   "category": "과일"},
    # 수산물
    "601": {"item_name": "고등어/국산",   "unit": "1손",   "category": "수산물"},
    "602": {"item_name": "갈치/국산",     "unit": "1마리", "category": "수산물"},
    "603": {"item_name": "오징어/국산",   "unit": "1마리", "category": "수산물"},
    "604": {"item_name": "꽃게/암꽃게",   "unit": "1kg",   "category": "수산물"},
    "605": {"item_name": "흰다리새우",    "unit": "500g",  "category": "수산물"},
    "606": {"item_name": "광어회/활어",   "unit": "300g",  "category": "수산물"},
    "607": {"item_name": "굴/생굴",       "unit": "500g",  "category": "수산물"},
    # 육류
    "501": {"item_name": "한우/등심",     "unit": "200g",  "category": "육류"},
    "502": {"item_name": "한우/갈비",     "unit": "600g",  "category": "육류"},
    "503": {"item_name": "삼겹살/국산",   "unit": "600g",  "category": "육류"},
    "504": {"item_name": "목살/국산",     "unit": "500g",  "category": "육류"},
    "505": {"item_name": "닭다리살",      "unit": "500g",  "category": "육류"},
    "506": {"item_name": "닭가슴살",      "unit": "500g",  "category": "육류"},
    "507": {"item_name": "소불고기/양념", "unit": "500g",  "category": "육류"},
}

# 상품명 → KAMIS 코드 매칭 (2자 이상만 — 단음절은 오매칭 위험으로 제외)
# '감자/감기/배 5개' 등이 '감/단감/배/신고'로 잘못 잡히는 것을 방지.
PRODUCT_KAMIS_KEYWORDS: dict[str, str] = {
    # 채소
    "배추": "112", "당근": "152", "양파": "153", "대파": "154",
    "마늘": "155", "청양고추": "156", "고추": "156", "시금치": "157",
    # 과일
    "사과": "214", "후지": "214", "신고배": "215", "신고": "215",
    "감귤": "216", "샤인머스캣": "217", "샤인": "217", "머스캣": "217",
    "딸기": "218", "수박": "219", "단감": "421", "복숭아": "422",
    # 수산물
    "고등어": "601", "갈치": "602", "오징어": "603", "꽃게": "604",
    "새우": "605", "광어": "606",
    # 육류
    "등심": "501", "갈비": "502", "삼겹살": "503", "목살": "504",
    "닭다리": "505", "닭가슴": "506", "닭날개": "505", "불고기": "507",
    "한우": "501",  # 한우 단독 → 등심 (cf. '한우 갈비'는 '갈비'가 우선 매칭)
}


# ──────────────────────────────────────────────
# KAMIS API 호출
# ──────────────────────────────────────────────

def _fetch_kamis_price(kamis_item_code: str) -> Optional[dict]:
    """
    KAMIS 소매가격 API 호출.
    성공 시 {"retail_price": int, "prev_day_price": int, ...} 반환.
    실패 시 None 반환 (fallback).
    """
    api_key = os.getenv("KAMIS_API_KEY", "")
    api_id  = os.getenv("KAMIS_API_ID", "test")

    if not api_key:
        logger.warning("KAMIS_API_KEY 미설정 — fallback 모드")
        return None

    today = date.today().strftime("%Y-%m-%d")
    params = {
        "action":       "dailySalesList",
        "p_cert_key":   api_key,
        "p_cert_id":    api_id,
        "p_returntype": "json",
        "p_itemcategorycode": "100",   # 식량작물/채소/과일 포함 카테고리
        "p_itemcode":         kamis_item_code,
        "p_kindcode":         "01",
        "p_productrankcode":  "04",    # 상품
        "p_countrycode":      "1101",  # 서울
        "p_convert_kg_yn":    "N",
        "p_startday":         today,
        "p_endday":           today,
    }
    try:
        resp = httpx.get(KAMIS_BASE_URL, params=params, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        items = (
            data.get("data", {})
                .get("item", [])
        )
        if not items:
            return None
        row = items[0]

        def _to_int(val) -> Optional[int]:
            try:
                return int(str(val).replace(",", ""))
            except (ValueError, TypeError):
                return None

        return {
            "retail_price":     _to_int(row.get("dpr1")),
            "prev_day_price":   _to_int(row.get("dpr2")),
            "prev_month_price": _to_int(row.get("dpr3")),
            "prev_year_price":  _to_int(row.get("dpr4")),
        }
    except Exception as e:
        logger.error("KAMIS 호출 실패: %s", e)
        return None


# ──────────────────────────────────────────────
# 시세 저장 / 조회
# ──────────────────────────────────────────────

def sync_kamis_price(db: Session, kamis_item_code: str) -> dict:
    """
    KAMIS에서 오늘 가격을 가져와 MarketPrice에 저장하고 결과를 반환.
    API 실패 시 최근 저장된 값을 사용 (fallback).
    """
    item_meta = KAMIS_ITEM_MAP.get(kamis_item_code)
    if not item_meta:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 품목코드: {kamis_item_code}")

    price_data = _fetch_kamis_price(kamis_item_code)
    fallback   = price_data is None

    if fallback:
        # DB에 기존 값이 있으면 반환
        existing = repo.get_latest_market_price(db, kamis_item_code)
        if existing:
            return _format_market_price(existing, fallback=True)
        # 아예 없으면 mock
        price_data = {"retail_price": None, "prev_day_price": None,
                      "prev_month_price": None, "prev_year_price": None}

    mp = repo.upsert_market_price(
        db,
        item_name        = item_meta["item_name"],
        kamis_item_code  = kamis_item_code,
        unit             = item_meta["unit"],
        price_date       = date.today(),
        retail_price     = price_data["retail_price"],
        prev_day_price   = price_data.get("prev_day_price"),
        prev_month_price = price_data.get("prev_month_price"),
        prev_year_price  = price_data.get("prev_year_price"),
    )
    return _format_market_price(mp, fallback=fallback)


def get_market_price(db: Session, kamis_item_code: str) -> dict:
    mp = repo.get_latest_market_price(db, kamis_item_code)
    if not mp:
        raise HTTPException(status_code=404, detail="시세 데이터가 없습니다. 먼저 sync를 실행하세요.")
    return _format_market_price(mp, fallback=False)


def _format_market_price(mp, fallback: bool) -> dict:
    return {
        "market_price_id":  mp.market_price_id,
        "item_name":        mp.item_name,
        "kamis_item_code":  mp.kamis_item_code,
        "unit":             mp.unit,
        "price_date":       mp.price_date.isoformat() if mp.price_date else None,
        "retail_price":     mp.retail_price,
        "prev_day_price":   mp.prev_day_price,
        "prev_month_price": mp.prev_month_price,
        "prev_year_price":  mp.prev_year_price,
        "fallback_mode":    fallback,
    }


# ──────────────────────────────────────────────
# Product 가격 자동 업데이트
# ──────────────────────────────────────────────

def update_product_price_from_kamis(
    db: Session, user, product_id: str, kamis_item_code: str
) -> dict:
    """
    KAMIS 소매가를 기준으로 Product.price를 업데이트하고
    ProductPriceHistory에 이력을 기록한다.
    merchant 권한 검증은 호출 측(router/service)에서 수행하며,
    여기서는 본인 점포 상품 여부도 검증한다.
    """
    product: Optional[Product] = (
        db.query(Product).filter(Product.product_id == product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    from app.db.repositories.merchant_repository import get_store_ids_for_user
    store_ids = get_store_ids_for_user(db, user.user_id)
    if product.store_id not in store_ids:
        raise HTTPException(status_code=403, detail="해당 상품에 대한 권한이 없습니다.")

    # 시세 동기화 (실패 시 HTTPException 또는 fallback)
    price_info = sync_kamis_price(db, kamis_item_code)

    new_price = price_info.get("retail_price")
    if new_price is None:
        raise HTTPException(
            status_code=503,
            detail="KAMIS 시세 데이터가 없어 가격을 업데이트할 수 없습니다.",
        )

    old_price = product.price
    # 최신 MarketPrice id를 reference로 기록
    mp = repo.get_latest_market_price(db, kamis_item_code)
    repo.record_price_change(
        db,
        product_id   = product_id,
        old_price    = old_price,
        new_price    = new_price,
        reason       = PriceChangeReasonEnum.kamis,
        reference_id = mp.market_price_id if mp else None,
    )
    repo.update_product_price(db, product, new_price)

    return {
        "product_id": product_id,
        "old_price":  old_price,
        "new_price":  new_price,
        "kamis_item_code": kamis_item_code,
        "price_date": price_info.get("price_date"),
        "fallback_mode": price_info.get("fallback_mode", False),
    }


def get_price_history(db: Session, product_id: str, limit: int = 30, user=None) -> dict:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    if user is not None:
        from app.db.repositories.merchant_repository import get_store_ids_for_user
        store_ids = get_store_ids_for_user(db, user.user_id)
        if product.store_id not in store_ids:
            raise HTTPException(status_code=403, detail="해당 상품에 대한 권한이 없습니다.")

    histories = repo.get_price_history(db, product_id, limit)
    def _item(h):
        change_amount = (h.new_price or 0) - (h.old_price or 0)
        change_rate = None
        if h.old_price:
            change_rate = round(change_amount / h.old_price * 100, 1)
        return {
            "history_id":    h.history_id,
            "old_price":     h.old_price,
            "new_price":     h.new_price,
            "change_amount": change_amount,
            "change_rate":   change_rate,
            "reason":        h.reason.value,
            "reference_id":  h.reference_id,
            "created_at":    h.created_at.isoformat() if h.created_at else None,
        }
    return {
        "product_id": product_id,
        "items": [_item(h) for h in histories],
    }


# ──────────────────────────────────────────────
# 대시보드 가격 정책 보조 문구
# ──────────────────────────────────────────────

def get_price_suggestion(
    db: Session, store_ids: list[str]
) -> list[dict]:
    """
    상인 대시보드용: 등록 상품 vs KAMIS 시세 비교 → 가격 제안 문구 반환.
    KAMIS 연동이 없을 경우 보조 문구만 반환.
    """
    from app.db.models.product import Product
    products = (
        db.query(Product)
        .filter(Product.store_id.in_(store_ids))
        .all()
    )
    suggestions = []
    for p in products:
        suggestion = _build_price_suggestion(db, p)
        if suggestion:
            suggestions.append(suggestion)
    return suggestions


def _build_price_suggestion(db: Session, product: Product) -> Optional[dict]:
    """품목명으로 KAMIS 코드 추정 후 시세 비교."""
    # 1) 우선 PRODUCT_KAMIS_KEYWORDS 사전 (긴 키부터)
    code_match: Optional[str] = None
    for keyword in sorted(PRODUCT_KAMIS_KEYWORDS, key=len, reverse=True):
        if keyword in product.product_name:
            code_match = PRODUCT_KAMIS_KEYWORDS[keyword]
            break
    # 2) fallback: KAMIS_ITEM_MAP item_name 앞부분 (단, 2자 이상만 — 오매칭 방지)
    if not code_match:
        for code, meta in KAMIS_ITEM_MAP.items():
            keyword = meta["item_name"].split("/")[0]
            if len(keyword) >= 2 and keyword in product.product_name:
                code_match = code
                break

    if not code_match:
        return None

    mp = repo.get_latest_market_price(db, code_match)
    if not mp or mp.retail_price is None:
        return None

    diff_pct = round((product.price - mp.retail_price) / mp.retail_price * 100, 1)
    if diff_pct > 10:
        advice = f"현재 가격이 시세보다 {diff_pct}% 높습니다. 인하를 검토해 보세요."
    elif diff_pct < -10:
        advice = f"현재 가격이 시세보다 {abs(diff_pct)}% 낮습니다. 인상 여지가 있습니다."
    else:
        advice = f"현재 가격이 시세와 유사합니다 (±{abs(diff_pct)}%)."

    return {
        "product_id":   product.product_id,
        "product_name": product.product_name,
        "current_price": product.price,
        "market_price":  mp.retail_price,
        "price_date":    mp.price_date.isoformat(),
        "diff_pct":      diff_pct,
        "advice":        advice,
    }
