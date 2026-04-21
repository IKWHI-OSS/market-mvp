import enum
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class RoleEnum(str, enum.Enum):
    consumer = "consumer"
    merchant = "merchant"
    operator = "operator"


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    home_market_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
