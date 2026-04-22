from typing import Optional
from pydantic import BaseModel


class ShoppingListCreate(BaseModel):
    title: str


class ShoppingListItemCreate(BaseModel):
    product_name_snapshot: str
    qty: int
    unit: str
    product_id: Optional[str] = None
    estimated_price: Optional[int] = None
    store_id: Optional[str] = None


class ShoppingListItemPatch(BaseModel):
    checked: Optional[bool] = None
    qty: Optional[int] = None
