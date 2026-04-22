from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.repositories import shopping_list_repository as repo


def _list_out(sl) -> dict:
    return {
        "shopping_list_id": sl.shopping_list_id,
        "title": sl.title,
        "total_estimated_price": sl.total_estimated_price,
        "item_count": len(sl.items),
        "created_at": sl.created_at.isoformat() if sl.created_at else None,
    }


def _item_out(item) -> dict:
    return {
        "list_item_id": item.list_item_id,
        "shopping_list_id": item.shopping_list_id,
        "product_name_snapshot": item.product_name_snapshot,
        "qty": item.qty,
        "unit": item.unit,
        "checked": item.checked,
        "estimated_price": item.estimated_price,
    }


def get_shopping_lists(db: Session, user_id: str) -> list:
    lists = repo.get_lists_by_user(db, user_id)
    return [_list_out(sl) for sl in lists]


def create_shopping_list(db: Session, user_id: str, title: str) -> dict:
    sl = repo.create_list(db, user_id, title)
    return _list_out(sl)


def add_item(db: Session, shopping_list_id: str, user_id: str,
             product_name_snapshot: str, qty: int, unit: str,
             product_id=None, estimated_price=None, store_id=None) -> dict:
    sl = repo.get_list_by_id(db, shopping_list_id, user_id)
    if not sl:
        raise HTTPException(status_code=404, detail="장보기 리스트를 찾을 수 없습니다.")
    item = repo.create_item(db, shopping_list_id, product_name_snapshot, qty, unit,
                            product_id, estimated_price, store_id)
    return _item_out(item)


def patch_item(db: Session, shopping_list_id: str, list_item_id: str, user_id: str,
               checked: Optional[bool], qty: Optional[int]) -> dict:
    sl = repo.get_list_by_id(db, shopping_list_id, user_id)
    if not sl:
        raise HTTPException(status_code=404, detail="장보기 리스트를 찾을 수 없습니다.")
    item = repo.get_item(db, shopping_list_id, list_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    item = repo.update_item(db, item, checked, qty)
    return _item_out(item)


def remove_item(db: Session, shopping_list_id: str, list_item_id: str, user_id: str) -> dict:
    sl = repo.get_list_by_id(db, shopping_list_id, user_id)
    if not sl:
        raise HTTPException(status_code=404, detail="장보기 리스트를 찾을 수 없습니다.")
    item = repo.get_item(db, shopping_list_id, list_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    repo.delete_item(db, item)
    return {"deleted": True}
