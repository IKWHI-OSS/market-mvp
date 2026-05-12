from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.drop_event import DropStatusEnum
from app.db.models.product import StockStatusEnum
from app.db.models.market_price import PriceChangeReasonEnum
from app.db.repositories import merchant_repository as repo
from app.db.repositories import price_repository
from app.services.drop_service import trigger_drop_status_notifications


def _require_merchant(user):
    if user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="상인 권한이 필요합니다.")


def get_dashboard(db: Session, user) -> dict:
    _require_merchant(user)
    store_ids = repo.get_store_ids_for_user(db, user.user_id)
    return {
        "today_product_count": repo.count_products(db, store_ids),
        "risk_stock_count": repo.count_risk_stock(db, store_ids),
        "pending_request_count": 0,
        "today_drop_count": repo.count_today_drops(db, store_ids),
    }


def create_product(db: Session, user, store_id: str, product_name: str, price: int,
                   stock_status: str, category=None, image_url=None, quality_note=None) -> dict:
    _require_merchant(user)
    try:
        status_enum = StockStatusEnum(stock_status)
    except ValueError:
        raise HTTPException(status_code=422, detail="stock_status 값이 유효하지 않습니다.")
    p = repo.create_product(db, store_id, product_name, price, status_enum, category, image_url, quality_note)
    return {
        "product_id": p.product_id,
        "store_id": p.store_id,
        "product_name": p.product_name,
        "price": p.price,
        "stock_status": p.stock_status.value,
        "category": p.category,
        "image_url": p.image_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _mock_ai_draft(store_id: str, image_url=None, voice_text=None) -> dict:
    return {
        "product_name": "추천 상품",
        "category": "기타",
        "description": "AI가 분석한 상품 설명입니다.",
    }


def ai_draft(db: Session, user, store_id: str, image_url=None, voice_text=None,
             ai_fn=None) -> dict:
    _require_merchant(user)
    if ai_fn is None:
        ai_fn = _mock_ai_draft
    try:
        draft = ai_fn(store_id=store_id, image_url=image_url, voice_text=voice_text)
        return {"draft": draft, "fallback_mode": False}
    except Exception:
        return {"draft": {}, "fallback_mode": True}


def get_price_suggestions(db: Session, user) -> list:
    """대시보드용 가격 정책 보조 응답 (KAMIS 시세 비교)."""
    _require_merchant(user)
    store_ids = repo.get_store_ids_for_user(db, user.user_id)
    from app.services.price_service import get_price_suggestion
    return get_price_suggestion(db, store_ids)


def update_product(db: Session, user, product_id: str,
                   price: Optional[int], stock_status: Optional[str]) -> dict:
    _require_merchant(user)
    product = repo.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    store_ids = repo.get_store_ids_for_user(db, user.user_id)
    if product.store_id not in store_ids:
        raise HTTPException(status_code=403, detail="해당 상품에 대한 권한이 없습니다.")

    if price is not None and price != product.price:
        price_repository.record_price_change(
            db,
            product_id=product_id,
            old_price=product.price,
            new_price=price,
            reason=PriceChangeReasonEnum.manual,
        )
        product.price = price

    if stock_status is not None:
        try:
            product.stock_status = StockStatusEnum(stock_status)
        except ValueError:
            raise HTTPException(status_code=422, detail="stock_status 값이 유효하지 않습니다.")

    db.commit()
    db.refresh(product)
    return {
        "product_id": product.product_id,
        "store_id": product.store_id,
        "product_name": product.product_name,
        "price": product.price,
        "stock_status": product.stock_status.value,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def get_my_store(db: Session, user) -> dict:
    _require_merchant(user)
    store = repo.get_first_store_for_user(db, user.user_id)
    if not store:
        raise HTTPException(status_code=404, detail="등록된 가게가 없습니다.")
    return {
        "store_id": store.store_id,
        "store_name": store.store_name,
        "zone_label": store.zone_label,
        "market_id": store.market_id,
    }


def update_drop_status(db: Session, user, drop_id: str, new_status: str) -> dict:
    _require_merchant(user)
    try:
        status_enum = DropStatusEnum(new_status)
    except ValueError:
        raise HTTPException(status_code=422, detail="status 값이 유효하지 않습니다.")
    drop = repo.get_drop_by_id(db, drop_id)
    if not drop:
        raise HTTPException(status_code=404, detail="드랍을 찾을 수 없습니다.")
    if drop.status == status_enum:
        raise HTTPException(status_code=409, detail="이미 동일한 상태입니다.")
    drop = repo.update_drop_status(db, drop, status_enum)
    trigger_drop_status_notifications(db, drop)
    return {"drop_id": drop.drop_id, "status": drop.status.value}
