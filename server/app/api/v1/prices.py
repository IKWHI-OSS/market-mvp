"""
가격/재고 고도화 API
  GET  /prices/market/{kamis_item_code}          — 최신 KAMIS 시세 조회
  POST /prices/market/{kamis_item_code}/sync     — KAMIS 시세 동기화 (merchant)
  POST /merchant/products/{product_id}/price     — KAMIS 기반 상품 가격 자동 업데이트 (merchant)
  GET  /merchant/products/{product_id}/price-history — 가격 변경 이력 (merchant)
  GET  /merchant/dashboard/price-suggestions     — 가격 정책 보조 문구 (merchant)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import price_service, merchant_service
from app.services.auth_service import get_current_user

router = APIRouter(tags=["prices"])


# ── 공개 시세 조회 ───────────────────────────────────────────────────

@router.get("/prices/market/{kamis_item_code}", response_model=BaseResponse)
def get_market_price(
    kamis_item_code: str,
    db: Session = Depends(get_db),
):
    """최근 저장된 KAMIS 시세 반환."""
    data = price_service.get_market_price(db, kamis_item_code)
    return success_response(data)


@router.post("/prices/market/{kamis_item_code}/sync", response_model=BaseResponse)
def sync_market_price(
    kamis_item_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """KAMIS API를 호출해 오늘 가격을 저장/갱신 (로그인 필요)."""
    data = price_service.sync_kamis_price(db, kamis_item_code)
    return success_response(data)


# ── 상인 전용 ───────────────────────────────────────────────────────

@router.post(
    "/merchant/products/{product_id}/price",
    response_model=BaseResponse,
)
def update_product_price(
    product_id: str,
    kamis_item_code: str = Query(..., description="KAMIS 품목코드"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """KAMIS 소매가로 상품 가격 자동 업데이트 + 이력 기록."""
    # merchant 권한 검증
    if current_user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="상인 권한이 필요합니다.")
    data = price_service.update_product_price_from_kamis(
        db, current_user, product_id, kamis_item_code
    )
    return success_response(data)


@router.get(
    "/merchant/products/{product_id}/price-history",
    response_model=BaseResponse,
)
def get_price_history(
    product_id: str,
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """상품 가격 변경 이력 조회."""
    if current_user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="상인 권한이 필요합니다.")
    data = price_service.get_price_history(db, product_id, limit)
    return success_response(data)


@router.get(
    "/merchant/dashboard/price-suggestions",
    response_model=BaseResponse,
)
def price_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """등록 상품 vs KAMIS 시세 비교 → 가격 정책 보조 문구."""
    data = merchant_service.get_price_suggestions(db, current_user)
    return success_response({"suggestions": data})
