from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.repositories.product_repository import search_products, get_product_with_store


def get_products_search(db, q, market_id=None, sort="latest", stock_status=None, page=1, size=20):
    size = min(size, 100)
    rows, total = search_products(db, q, market_id, sort, stock_status, page, size)
    items = [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "price": p.price,
            "stock_status": p.stock_status.value,
            "image_url": p.image_url,
            "store_id": s.store_id,
            "store_name": s.store_name,
            "zone_label": s.zone_label,
        }
        for p, s in rows
    ]
    return {
        "items": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "has_next": (page * size) < total,
        },
    }


def get_product_detail(db, product_id):
    row = get_product_with_store(db, product_id)
    if not row:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    p, s = row
    return {
        "product_id": p.product_id,
        "product_name": p.product_name,
        "price": p.price,
        "stock_status": p.stock_status.value,
        "image_url": p.image_url,
        "quality_note": p.quality_note,
        "category": p.category,
        "store": {
            "store_id": s.store_id,
            "store_name": s.store_name,
            "zone_label": s.zone_label,
            "market_id": s.market_id,
        },
    }
