from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.repositories.catalog_repository import (
    get_event_detail,
    get_store_by_id,
    get_store_spotlight_image,
)


def get_event(db: Session, catalog_item_id: str) -> dict:
    row = get_event_detail(db, catalog_item_id)
    if not row:
        raise HTTPException(status_code=404, detail="행사를 찾을 수 없습니다.")
    item, store = row
    return {
        "catalog_item_id": item.catalog_item_id,
        "title": item.title,
        "description": item.title_snapshot,
        "image_url": item.image_snapshot,
        "store_id": item.store_id,
        "store_name": store.store_name if store else None,
        "zone_label": store.zone_label if store else None,
        "valid_from": item.start_at.isoformat() if item.start_at else None,
        "valid_until": item.end_at.isoformat() if item.end_at else None,
    }


def get_store_spotlight_detail(db: Session, store_id: str) -> dict:
    store = get_store_by_id(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="점포를 찾을 수 없습니다.")
    image_url = get_store_spotlight_image(db, store_id)
    products = [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "price": p.price,
            "stock_status": p.stock_status.value,
        }
        for p in store.products
    ]
    return {
        "store_id": store.store_id,
        "store_name": store.store_name,
        "summary": store.store_story_summary or "",
        "description": store.store_story_summary or "",
        "image_url": image_url,
        "zone_label": store.zone_label,
        "products": products,
    }
