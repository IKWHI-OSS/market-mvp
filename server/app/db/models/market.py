from sqlalchemy import Column, String, DECIMAL, Text, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class Market(Base):
    __tablename__ = "Market"

    market_id = Column(String(36), primary_key=True)
    market_name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    lat = Column(DECIMAL(10, 7), nullable=False)
    lng = Column(DECIMAL(10, 7), nullable=False)
    region_code = Column(String(20), nullable=True)
    zoom = Column(DECIMAL(5, 2), nullable=False)
    market_desc = Column(Text, nullable=True)
    open_hours = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
