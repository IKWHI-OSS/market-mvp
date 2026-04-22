"""
price_repository — MarketPrice / ProductPriceHistory CRUD
"""
import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.market_price import MarketPrice, ProductPriceHistory, PriceChangeReasonEnum
from app.db.models.product import Product


# ──────────────────────────────────────────────
# MarketPrice
# ──────────────────────────────────────────────

def upsert_market_price(
    db: Session,
    *,
    item_name: str,
    kamis_item_code: str,
    unit: str,
    price_date: date,
    retail_price: Optional[int],
    prev_day_price: Optional[int] = None,
    prev_month_price: Optional[int] = None,
    prev_year_price: Optional[int] = None,
) -> MarketPrice:
    """UNIQUE KEY (kamis_item_code, item_name, price_date) 기준 upsert."""
    existing = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.kamis_item_code == kamis_item_code,
            MarketPrice.item_name == item_name,
            MarketPrice.price_date == price_date,
        )
        .first()
    )
    if existing:
        existing.retail_price     = retail_price
        existing.prev_day_price   = prev_day_price
        existing.prev_month_price = prev_month_price
        existing.prev_year_price  = prev_year_price
        db.commit()
        db.refresh(existing)
        return existing

    mp = MarketPrice(
        market_price_id  = str(uuid.uuid4()),
        item_name        = item_name,
        kamis_item_code  = kamis_item_code,
        unit             = unit,
        price_date       = price_date,
        retail_price     = retail_price,
        prev_day_price   = prev_day_price,
        prev_month_price = prev_month_price,
        prev_year_price  = prev_year_price,
    )
    db.add(mp)
    db.commit()
    db.refresh(mp)
    return mp


def get_latest_market_price(
    db: Session, kamis_item_code: str
) -> Optional[MarketPrice]:
    return (
        db.query(MarketPrice)
        .filter(MarketPrice.kamis_item_code == kamis_item_code)
        .order_by(MarketPrice.price_date.desc())
        .first()
    )


def list_market_prices(db: Session, kamis_item_code: str, limit: int = 30) -> list:
    return (
        db.query(MarketPrice)
        .filter(MarketPrice.kamis_item_code == kamis_item_code)
        .order_by(MarketPrice.price_date.desc())
        .limit(limit)
        .all()
    )


# ──────────────────────────────────────────────
# ProductPriceHistory
# ──────────────────────────────────────────────

def record_price_change(
    db: Session,
    *,
    product_id: str,
    old_price: int,
    new_price: int,
    reason: PriceChangeReasonEnum = PriceChangeReasonEnum.manual,
    reference_id: Optional[str] = None,
) -> ProductPriceHistory:
    h = ProductPriceHistory(
        history_id   = str(uuid.uuid4()),
        product_id   = product_id,
        old_price    = old_price,
        new_price    = new_price,
        reason       = reason,
        reference_id = reference_id,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def update_product_price(db: Session, product: Product, new_price: int) -> Product:
    product.price = new_price
    db.commit()
    db.refresh(product)
    return product


def get_price_history(
    db: Session, product_id: str, limit: int = 30
) -> list:
    return (
        db.query(ProductPriceHistory)
        .filter(ProductPriceHistory.product_id == product_id)
        .order_by(ProductPriceHistory.created_at.desc())
        .limit(limit)
        .all()
    )
