from typing import Optional

from sqlalchemy.orm import Session

from app.db.repositories.home_repository import (
    get_drop_hero,
    get_event_cards,
    get_market,
    get_store_spotlights,
)


def get_home_feed(db: Session, market_id: Optional[str] = None) -> dict:
    drops = get_drop_hero(db, market_id)
    events = get_event_cards(db, market_id)
    spotlights = get_store_spotlights(db, market_id)
    market = get_market(db, market_id) if market_id else None

    drop_hero = [
        {
            "drop_id": drop.drop_id,
            "product_id": drop.product_id,
            "store_id": drop.store_id,
            "title": drop.title,
            "image_url": image_url,
            "status": drop.status.value,
            "expected_at": drop.expected_at.isoformat(),
        }
        for drop, image_url in drops
    ]

    event_cards = [
        {
            "catalog_item_id": c.catalog_item_id,
            "title": c.title,
            "image_url": c.image_snapshot,
        }
        for c in events
    ]

    store_spotlights = [
        {
            "store_id": c.store_id,
            "store_name": store_name,
            "summary": c.title_snapshot,
            "image_url": c.image_snapshot,
        }
        for c, store_name in spotlights
    ]

    return {
        "market": (
            {"market_id": market.market_id, "market_name": market.market_name}
            if market
            else None
        ),
        "drop_hero": drop_hero,
        "event_cards": event_cards,
        "store_spotlights": store_spotlights,
    }
