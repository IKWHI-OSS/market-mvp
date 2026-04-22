from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.notification import Notification


def list_notifications(
    db: Session,
    user_id: str,
    is_read: Optional[bool] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list, int]:
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    query = query.order_by(Notification.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total


def get_notification(
    db: Session, notification_id: str, user_id: str
) -> Optional[Notification]:
    return (
        db.query(Notification)
        .filter(
            Notification.notification_id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )


def mark_as_read(db: Session, notif: Notification) -> Notification:
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
