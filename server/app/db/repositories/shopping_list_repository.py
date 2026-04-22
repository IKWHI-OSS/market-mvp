import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.shopping_list import ShoppingList
from app.db.models.shopping_list_item import ShoppingListItem


def get_lists_by_user(db: Session, user_id: str) -> list:
    return (
        db.query(ShoppingList)
        .filter(ShoppingList.user_id == user_id)
        .order_by(ShoppingList.created_at.desc())
        .all()
    )


def create_list(db: Session, user_id: str, title: str) -> ShoppingList:
    sl = ShoppingList(
        shopping_list_id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
    )
    db.add(sl)
    db.commit()
    db.refresh(sl)
    return sl


def get_list_by_id(db: Session, shopping_list_id: str, user_id: str) -> Optional[ShoppingList]:
    return (
        db.query(ShoppingList)
        .filter(
            ShoppingList.shopping_list_id == shopping_list_id,
            ShoppingList.user_id == user_id,
        )
        .first()
    )


def create_item(db: Session, shopping_list_id: str, product_name_snapshot: str, qty: int, unit: str,
                product_id=None, estimated_price=None, store_id=None) -> ShoppingListItem:
    item = ShoppingListItem(
        list_item_id=str(uuid.uuid4()),
        shopping_list_id=shopping_list_id,
        product_name_snapshot=product_name_snapshot,
        qty=qty,
        unit=unit,
        product_id=product_id,
        estimated_price=estimated_price,
        store_id=store_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, shopping_list_id: str, list_item_id: str) -> Optional[ShoppingListItem]:
    return (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.shopping_list_id == shopping_list_id,
            ShoppingListItem.list_item_id == list_item_id,
        )
        .first()
    )


def update_item(db: Session, item: ShoppingListItem, checked: Optional[bool] = None,
                qty: Optional[int] = None) -> ShoppingListItem:
    if checked is not None:
        item.checked = checked
    if qty is not None:
        item.qty = qty
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: ShoppingListItem) -> None:
    db.delete(item)
    db.commit()
