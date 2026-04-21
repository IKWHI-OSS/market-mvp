from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Merchant(Base):
    __tablename__ = "Merchant"

    merchant_id = Column(String(36), primary_key=True)
    store_id = Column(String(36), ForeignKey("Store.store_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("User.user_id"), nullable=False)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="merchants")
    user = relationship("User", backref="merchant_profile")
