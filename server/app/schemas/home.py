from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DropHeroItem(BaseModel):
    drop_id: str
    product_id: str
    store_id: str
    title: Optional[str]
    image_url: Optional[str]
    status: str
    expected_at: str


class EventCard(BaseModel):
    catalog_item_id: str
    title: str
    image_url: str


class StoreSpotlight(BaseModel):
    store_id: str
    store_name: str
    summary: str
    image_url: str


class HomeData(BaseModel):
    market: Optional[Dict[str, Any]]
    drop_hero: List[DropHeroItem]
    event_cards: List[EventCard]
    store_spotlights: List[StoreSpotlight]
