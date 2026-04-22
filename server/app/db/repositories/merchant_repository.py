import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.merchant import Merchant
from app.db.models.product import Product, StockStatusEnum
from app.db.models.drop_event import DropEvent, DropStatusEnum
from app.db.models.store import Store


def get_store_ids_for_user(db: Session, user_id: str) -> list:
    rows = db.query(Merchant.store_id).filter(Merchant.user_id == user_id).all()
    return [r[0] for r in rows]


def count_products(db: Session, store_ids: list) -> int:
    if not store_ids:
        return 0
    return db.query(Product).filter(Product.store_id.in_(store_ids)).count()


def count_risk_stock(db: Session, store_ids: list) -> int:
    if not store_ids:
        return 0
    return (
        db.query(Product)
        .filter(Product.store_id.in_(store_ids), Product.stock_status == StockStatusEnum.low_stock)
        .count()
    )


def count_today_drops(db: Session, store_ids: list) -> int:
    if not store_ids:
        return 0
    return (
        db.query(DropEvent)
        .filter(
            DropEvent.store_id.in_(store_ids),
            DropEvent.status.in_([DropStatusEnum.scheduled, DropStatusEnum.arrived]),
        )
        .count()
    )


def create_product(db: Session, store_id: str, product_name: str, price: int,
                   stock_status: StockStatusEnum, category=None, image_url=None,
                   quality_note=None) -> Product:
    p = Product(
        product_id=str(uuid.uuid4()),
        store_id=store_id,
        product_name=product_name,
        price=price,
        stock_status=stock_status,
        category=category,
        image_url=image_url,
        quality_note=quality_note,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_drop_by_id(db: Session, drop_id: str) -> Optional[DropEvent]:
    return db.query(DropEvent).filter(DropEvent.drop_id == drop_id).first()


def update_drop_status(db: Session, drop: DropEvent, new_status: DropStatusEnum) -> DropEvent:
    drop.status = new_status
    db.commit()
    db.refresh(drop)
    return drop
