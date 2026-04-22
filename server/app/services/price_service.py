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

# 품목코드 매핑 (MVP 기준 주요 농산물)
KAMIS_ITEM_MAP: dict[str, dict] = {
    "112": {"item_name": "배추/포기", "unit": "1포기"},
    "214": {"item_name": "사과/후지", "unit": "10개"},
    "215": {"item_name": "배/신고",   "unit": "10개"},
    "421": {"item_name": "감/단감",   "unit": "10개"},
    "151": {"item_name": "무/일반",   "unit": "1개"},
    "152": {"item_name": "당근",      "unit": "1kg"},
    "111": {"item_name": "쌀/20kg",   "unit": "20kg"},
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
    merchant 권한 검증은 호출 측(router/service)에서 수행한다.
    """
    product: Optional[Product] = (
        db.query(Product).filter(Product.product_id == product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

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


def get_price_history(db: Session, product_id: str, limit: int = 30) -> dict:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    histories = repo.get_price_history(db, product_id, limit)
    return {
        "product_id": product_id,
        "items": [
            {
                "history_id":   h.history_id,
                "old_price":    h.old_price,
                "new_price":    h.new_price,
                "reason":       h.reason.value,
                "reference_id": h.reference_id,
                "created_at":   h.created_at.isoformat() if h.created_at else None,
            }
            for h in histories
        ],
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
    # 품목명 → KAMIS 코드 fuzzy 매핑 (MVP 단순 키워드 매칭)
    code_match = None
    for code, meta in KAMIS_ITEM_MAP.items():
        keyword = meta["item_name"].split("/")[0]
        if keyword in product.product_name:
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
