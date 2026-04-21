from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ProductSearchItem(BaseModel):
    product_id: str
    product_name: str
    price: int
    stock_status: str
    image_url: Optional[str]
    store_id: str
    store_name: str
    zone_label: str


class ProductDetail(BaseModel):
    product_id: str
    product_name: str
    price: int
    stock_status: str
    image_url: Optional[str]
    quality_note: Optional[str]
    category: Optional[str]
    store: Dict[str, Any]


class Pagination(BaseModel):
    page: int
    size: int
    total: int
    has_next: bool


class ProductSearchData(BaseModel):
    items: List[ProductSearchItem]
    pagination: Pagination
