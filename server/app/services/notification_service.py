from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.repositories.notification_repository import (
    list_notifications,
    get_notification,
    mark_as_read,
)


def get_notifications(
    db: Session, user_id: str, is_read: Optional[bool], page: int, size: int
) -> dict:
    size = min(size, 100)
    items, total = list_notifications(db, user_id, is_read, page, size)
    return {
        "items": [
            {
                "notification_id": n.notification_id,
                "type": n.type,
                "title": n.title,
                "body": n.body,
                "target_type": n.target_type,
                "target_id": n.target_id,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ],
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "has_next": (page * size) < total,
        },
    }


def read_notification(db: Session, notification_id: str, user_id: str) -> dict:
    notif = get_notification(db, notification_id, user_id)
    if not notif:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")
    notif = mark_as_read(db, notif)
    return {"notification_id": notif.notification_id, "is_read": True}
