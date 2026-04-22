"""
preorder_repository — Preorder CRUD
"""
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.preorder import Preorder, PreorderStatusEnum


def create_preorder(
    db: Session,
    *,
    user_id: str,
    store_id: str,
    product_name: str,
    qty: int,
) -> Preorder:
    p = Preorder(
        preorder_id  = str(uuid.uuid4()),
        user_id      = user_id,
        store_id     = store_id,
        product_name = product_name,
        qty          = qty,
        status       = PreorderStatusEnum.requested,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def list_preorders_by_user(
    db: Session,
    user_id: str,
    page: int = 1,
    size: int = 20,
) -> tuple[list, int]:
    q = (
        db.query(Preorder)
        .filter(Preorder.user_id == user_id)
        .order_by(Preorder.created_at.desc())
    )
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return items, total


def list_preorders_by_store(
    db: Session,
    store_ids: list[str],
    page: int = 1,
    size: int = 20,
) -> tuple[list, int]:
    q = (
        db.query(Preorder)
        .filter(Preorder.store_id.in_(store_ids))
        .order_by(Preorder.created_at.desc())
    )
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return items, total


def get_preorder(db: Session, preorder_id: str) -> Optional[Preorder]:
    return db.query(Preorder).filter(Preorder.preorder_id == preorder_id).first()


def update_preorder_status(
    db: Session, preorder: Preorder, new_status: PreorderStatusEnum
) -> Preorder:
    preorder.status = new_status
    db.commit()
    db.refresh(preorder)
    return preorder
