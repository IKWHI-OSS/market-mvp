from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import catalog_service

router = APIRouter(tags=["stores"])


@router.get("/stores/{store_id}/spotlight", response_model=BaseResponse)
def get_store_spotlight(store_id: str, db: Session = Depends(get_db)):
    data = catalog_service.get_store_spotlight_detail(db, store_id)
    return success_response(data)


@router.get("/stores/{store_id}/products", response_model=BaseResponse)
def get_store_products(store_id: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.store_id == store_id).all()
    items = [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "price": p.price,
            "stock_status": p.stock_status.value,
            "category": p.category,
            "image_url": p.image_url,
        }
        for p in products
    ]
    return success_response({"items": items})
