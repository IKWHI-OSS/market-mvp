from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Notification(Base):
    __tablename__ = "Notification"

    notification_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("User.user_id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    target_screen_id = Column(String(50), nullable=True)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    send_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="notifications")
