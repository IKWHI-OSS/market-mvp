from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.catalog_item import CatalogItem, CatalogItemTypeEnum
from app.db.models.drop_event import DropEvent, DropStatusEnum
from app.db.models.market import Market
from app.db.models.product import Product
from app.db.models.store import Store


def get_drop_hero(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = (
        db.query(DropEvent, Product.image_url)
        .join(Product, DropEvent.product_id == Product.product_id)
        .filter(DropEvent.status.in_([DropStatusEnum.scheduled, DropStatusEnum.arrived]))
    )
    if market_id:
        query = query.join(Store, DropEvent.store_id == Store.store_id).filter(
            Store.market_id == market_id
        )
    return query.order_by(DropEvent.expected_at).limit(limit).all()


def get_event_cards(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = db.query(CatalogItem).filter(
        CatalogItem.item_type == CatalogItemTypeEnum.event
    )
    if market_id:
        query = query.filter(CatalogItem.market_id == market_id)
    return query.order_by(CatalogItem.priority.desc()).limit(limit).all()


def get_store_spotlights(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = (
        db.query(CatalogItem, Store.store_name)
        .join(Store, CatalogItem.store_id == Store.store_id)
        .filter(CatalogItem.item_type == CatalogItemTypeEnum.store_spotlight)
    )
    if market_id:
        query = query.filter(CatalogItem.market_id == market_id)
    return query.order_by(CatalogItem.priority.desc()).limit(limit).all()


def get_market(db: Session, market_id: str) -> Optional[Market]:
    return db.query(Market).filter(Market.market_id == market_id).first()
