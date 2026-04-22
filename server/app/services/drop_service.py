from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.drop_event import DropStatusEnum
from app.db.repositories import drop_repository

_STATUS_LABELS = {
    DropStatusEnum.arrived: "도착",
    DropStatusEnum.sold_out: "마감",
    DropStatusEnum.scheduled: "예정",
}


def get_drops(db, market_id=None, status=None, page=1, size=20, user_id=None):
    size = min(size, 100)
    rows, total = drop_repository.list_drops(db, market_id, status, page, size)
    drop_ids = [drop.drop_id for drop, _, _ in rows]
    subscribed_ids = (
        drop_repository.get_subscribed_drop_ids(db, user_id, drop_ids)
        if user_id
        else set()
    )
    items = [
        {
            "drop_id": drop.drop_id,
            "product_id": drop.product_id,
            "product_name": product_name,
            "store_id": drop.store_id,
            "store_name": store_name,
            "expected_at": drop.expected_at.isoformat(),
            "status": drop.status.value,
            "is_subscribed": drop.drop_id in subscribed_ids,
        }
        for drop, product_name, store_name in rows
    ]
    return {
        "items": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "has_next": (page * size) < total,
        },
    }


def subscribe_drop(db, drop_id: str, user_id: str) -> dict:
    drop = drop_repository.get_drop_by_id(db, drop_id)
    if not drop:
        raise HTTPException(status_code=404, detail="드랍을 찾을 수 없습니다.")
    existing = drop_repository.get_subscription(db, drop_id, user_id)
    if existing:
        raise HTTPException(status_code=409, detail="이미 구독 중인 드랍입니다.")
    drop_repository.create_subscription(db, drop_id, user_id)
    return {"drop_id": drop_id, "subscribed": True}


def unsubscribe_drop(db, drop_id: str, user_id: str) -> dict:
    drop = drop_repository.get_drop_by_id(db, drop_id)
    if not drop:
        raise HTTPException(status_code=404, detail="드랍을 찾을 수 없습니다.")
    sub = drop_repository.get_subscription(db, drop_id, user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="구독 중인 드랍이 아닙니다.")
    drop_repository.delete_subscription(db, sub)
    return {"drop_id": drop_id, "subscribed": False}


def trigger_drop_status_notifications(db: Session, drop_event) -> None:
    label = _STATUS_LABELS.get(drop_event.status, "변경")
    user_ids = drop_repository.get_subscriber_user_ids(db, drop_event.drop_id)
    for user_id in user_ids:
        drop_repository.create_notification(db, user_id, drop_event, label)
    db.commit()
