from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.product import Product, StockStatusEnum
from app.db.models.store import Store


def search_products(
    db: Session,
    q: str,
    market_id: Optional[str] = None,
    sort: str = "latest",
    stock_status: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list, int]:
    query = (
        db.query(Product, Store)
        .join(Store, Product.store_id == Store.store_id)
        .filter(Product.product_name.contains(q))
    )
    if market_id:
        query = query.filter(Store.market_id == market_id)
    if stock_status:
        query = query.filter(Product.stock_status == stock_status)
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    else:
        query = query.order_by(Product.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * size).limit(size).all()
    return rows, total


def get_product_with_store(db: Session, product_id: str):
    return (
        db.query(Product, Store)
        .join(Store, Product.store_id == Store.store_id)
        .filter(Product.product_id == product_id)
        .first()
    )
