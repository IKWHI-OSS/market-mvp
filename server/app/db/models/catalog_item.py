import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class CatalogItemTypeEnum(str, enum.Enum):
    drop = "drop"
    event = "event"
    store_spotlight = "store_spotlight"


class CatalogItem(Base):
    __tablename__ = "CatalogItem"

    catalog_item_id = Column(String(36), primary_key=True)
    market_id = Column(String(36), ForeignKey("Market.market_id"), nullable=False)
    store_id = Column(String(36), ForeignKey("Store.store_id"), nullable=True)
    product_id = Column(String(36), ForeignKey("Product.product_id"), nullable=True)
    item_type = Column(Enum(CatalogItemTypeEnum), nullable=False)
    title = Column(String(255), nullable=False)
    title_snapshot = Column(String(255), nullable=False)
    image_snapshot = Column(String(500), nullable=False)
    price_snapshot = Column(Integer, nullable=True)
    badge = Column(String(100), nullable=True)
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    market = relationship("Market", backref="catalog_items")
    store = relationship("Store", backref="catalog_items")
