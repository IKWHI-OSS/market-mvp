from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class RoutePlan(Base):
    __tablename__ = "RoutePlan"

    route_plan_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("User.user_id"), nullable=False)
    market_id = Column(String(36), ForeignKey("Market.market_id"), nullable=False)
    shopping_list_id = Column(
        String(36), ForeignKey("ShoppingList.shopping_list_id"), nullable=False
    )
    route_json = Column(JSON, nullable=False)
    estimated_minutes = Column(Integer, nullable=True)
    distance_meters = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="route_plans")
    market = relationship("Market", backref="route_plans")
