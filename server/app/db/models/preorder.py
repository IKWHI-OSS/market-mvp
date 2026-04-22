"""
Preorder — schema.sql의 Preorder 테이블과 1:1 매핑
status: requested / confirmed / ready / cancelled
"""
import enum
from sqlalchemy import Column, String, Integer, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class PreorderStatusEnum(str, enum.Enum):
    requested  = "requested"
    confirmed  = "confirmed"
    ready      = "ready"
    cancelled  = "cancelled"


class Preorder(Base):
    __tablename__ = "Preorder"

    preorder_id  = Column(String(36), primary_key=True)
    user_id      = Column(String(36), ForeignKey("User.user_id"),  nullable=False)
    store_id     = Column(String(36), ForeignKey("Store.store_id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    qty          = Column(Integer,     nullable=False)
    status       = Column(SAEnum(PreorderStatusEnum), nullable=False,
                          default=PreorderStatusEnum.requested)
    created_at   = Column(DateTime, server_default=func.now())

    user  = relationship("User",  backref="preorders")
    store = relationship("Store", backref="preorders")
