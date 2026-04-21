import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class StockStatusEnum(str, enum.Enum):
    in_stock = "in_stock"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"


class Product(Base):
    __tablename__ = "product"

    product_id = Column(String(36), primary_key=True)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    price = Column(Integer, nullable=False)
    stock_status = Column(
        Enum(StockStatusEnum), nullable=False, default=StockStatusEnum.in_stock
    )
    image_url = Column(String(500), nullable=True)
    quality_note = Column(Text, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="products")
    drop_events = relationship("DropEvent", back_populates="product")
