import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class DropStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    arrived = "arrived"
    sold_out = "sold_out"


class DropEvent(Base):
    __tablename__ = "drop_event"

    drop_id = Column(String(36), primary_key=True)
    product_id = Column(String(36), ForeignKey("product.product_id"), nullable=False)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=False)
    title = Column(String(255), nullable=True)
    expected_at = Column(DateTime, nullable=False)
    status = Column(Enum(DropStatusEnum), nullable=False, default=DropStatusEnum.scheduled)
    subscriber_count = Column(Integer, default=0)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="drop_events")
    store = relationship("Store", back_populates="drop_events")
