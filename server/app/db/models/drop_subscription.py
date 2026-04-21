from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base


class DropSubscription(Base):
    __tablename__ = "DropSubscription"

    subscription_id = Column(String(36), primary_key=True)
    drop_id = Column(String(36), ForeignKey("DropEvent.drop_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("User.user_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("drop_id", "user_id", name="uq_drop_subscription"),
    )
