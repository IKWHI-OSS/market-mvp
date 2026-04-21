from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=BaseResponse)
def search_products(
    q: str = Query(...),
    market_id: Optional[str] = Query(None),
    sort: str = Query("latest"),
    stock_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    data = product_service.get_products_search(db, q, market_id, sort, stock_status, page, size)
    return success_response(data)


@router.get("/{product_id}", response_model=BaseResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    data = product_service.get_product_detail(db, product_id)
    return success_response(data)
