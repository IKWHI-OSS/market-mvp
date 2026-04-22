"""
MarketPrice — KAMIS 농산물 시세 저장 테이블 (add_market_price.sql 동기화)
ProductPriceHistory — Product 가격 변경 이력
"""
import enum
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class MarketPrice(Base):
    __tablename__ = "MarketPrice"

    market_price_id  = Column(String(36), primary_key=True)
    item_name        = Column(String(100), nullable=False, comment="KAMIS 품목명")
    kamis_item_code  = Column(String(20),  nullable=False, comment="KAMIS 품목 코드")
    unit             = Column(String(50),  nullable=False, comment="단위")
    price_date       = Column(Date,        nullable=False, comment="가격 기준일")
    retail_price     = Column(Integer,     nullable=True,  comment="당일 소매가 dpr1")
    prev_day_price   = Column(Integer,     nullable=True,  comment="전일 가격 dpr2")
    prev_month_price = Column(Integer,     nullable=True,  comment="전월 가격 dpr3")
    prev_year_price  = Column(Integer,     nullable=True,  comment="전년 가격 dpr4")
    created_at       = Column(DateTime,    server_default=func.now())


class PriceChangeReasonEnum(str, enum.Enum):
    manual   = "manual"    # 상인 직접 수정
    kamis    = "kamis"     # KAMIS 시세 반영
    system   = "system"    # 시스템 자동


class ProductPriceHistory(Base):
    __tablename__ = "ProductPriceHistory"

    history_id    = Column(String(36), primary_key=True)
    product_id    = Column(String(36), ForeignKey("Product.product_id"), nullable=False)
    old_price     = Column(Integer,    nullable=False)
    new_price     = Column(Integer,    nullable=False)
    reason        = Column(SAEnum(PriceChangeReasonEnum), nullable=False,
                           default=PriceChangeReasonEnum.manual)
    reference_id  = Column(String(36), nullable=True, comment="KAMIS market_price_id 등")
    created_at    = Column(DateTime,   server_default=func.now())

    product = relationship("Product", backref="price_histories")
