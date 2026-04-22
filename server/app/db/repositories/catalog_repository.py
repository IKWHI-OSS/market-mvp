from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.catalog_item import CatalogItem, CatalogItemTypeEnum
from app.db.models.store import Store


def get_event_detail(db: Session, catalog_item_id: str):
    return (
        db.query(CatalogItem, Store)
        .outerjoin(Store, CatalogItem.store_id == Store.store_id)
        .filter(
            CatalogItem.catalog_item_id == catalog_item_id,
            CatalogItem.item_type == CatalogItemTypeEnum.event,
        )
        .first()
    )


def get_store_by_id(db: Session, store_id: str) -> Optional[Store]:
    return db.query(Store).filter(Store.store_id == store_id).first()


def get_store_spotlight_image(db: Session, store_id: str) -> Optional[str]:
    item = (
        db.query(CatalogItem.image_snapshot)
        .filter(
            CatalogItem.store_id == store_id,
            CatalogItem.item_type == CatalogItemTypeEnum.store_spotlight,
        )
        .first()
    )
    return item[0] if item else None
