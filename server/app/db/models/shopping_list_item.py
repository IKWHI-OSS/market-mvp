from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShoppingListItem(Base):
    __tablename__ = "ShoppingListItem"

    list_item_id = Column(String(36), primary_key=True)
    shopping_list_id = Column(
        String(36), ForeignKey("ShoppingList.shopping_list_id"), nullable=False
    )
    product_id = Column(String(36), ForeignKey("Product.product_id"), nullable=True)
    product_name_snapshot = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False)
    unit = Column(String(20), nullable=False)
    checked = Column(Boolean, default=False, nullable=False)
    estimated_price = Column(Integer, nullable=True)
    store_id = Column(String(36), ForeignKey("Store.store_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    shopping_list = relationship("ShoppingList", back_populates="items")
