from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.drop_event import DropStatusEnum
from app.db.models.product import StockStatusEnum
from app.db.repositories import merchant_repository as repo
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
