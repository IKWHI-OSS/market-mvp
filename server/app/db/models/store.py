from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Store(Base):
    __tablename__ = "store"

    store_id = Column(String(36), primary_key=True)
    market_id = Column(String(36), ForeignKey("market.market_id"), nullable=False)
    store_name = Column(String(255), nullable=False)
    zone_label = Column(String(50), nullable=False)
    lat = Column(DECIMAL(10, 7), nullable=True)
    lng = Column(DECIMAL(10, 7), nullable=True)
    phone = Column(String(20), nullable=True)
    status = Column(String(20), nullable=True, default="open")
    store_story_summary = Column(Text, nullable=True)
    open_hours = Column(String(255), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    market = relationship("Market", backref="stores")
    merchants = relationship("Merchant", back_populates="store")
    products = relationship("Product", back_populates="store")
    drop_events = relationship("DropEvent", back_populates="store")
