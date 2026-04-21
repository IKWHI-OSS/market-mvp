from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShoppingList(Base):
    __tablename__ = "ShoppingList"

    shopping_list_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("User.user_id"), nullable=False)
    title = Column(String(255), nullable=False)
    total_estimated_price = Column(Integer, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list")
