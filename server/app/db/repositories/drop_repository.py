import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.drop_event import DropEvent, DropStatusEnum
from app.db.models.drop_subscription import DropSubscription
from app.db.models.notification import Notification
from app.db.models.product import Product
from app.db.models.store import Store


def list_drops(db, market_id=None, status=None, page=1, size=20):
    query = (
        db.query(DropEvent, Product.product_name, Store.store_name)
        .join(Product, DropEvent.product_id == Product.product_id)
        .join(Store, DropEvent.store_id == Store.store_id)
    )
    if market_id:
        query = query.filter(Store.market_id == market_id)
    if status:
        query = query.filter(DropEvent.status == status)
    query = query.order_by(DropEvent.expected_at.asc())
    total = query.count()
    rows = query.offset((page - 1) * size).limit(size).all()
    return rows, total


def get_subscribed_drop_ids(db, user_id: str, drop_ids: list) -> set:
    if not drop_ids:
        return set()
    subs = (
        db.query(DropSubscription.drop_id)
        .filter(
            DropSubscription.user_id == user_id,
            DropSubscription.drop_id.in_(drop_ids),
        )
        .all()
    )
    return {s[0] for s in subs}


def get_drop_by_id(db, drop_id: str) -> Optional[DropEvent]:
    return db.query(DropEvent).filter(DropEvent.drop_id == drop_id).first()


def get_subscription(db, drop_id: str, user_id: str) -> Optional[DropSubscription]:
    return (
        db.query(DropSubscription)
        .filter(
            DropSubscription.drop_id == drop_id,
            DropSubscription.user_id == user_id,
        )
        .first()
    )


def create_subscription(db, drop_id: str, user_id: str) -> DropSubscription:
    sub = DropSubscription(
        subscription_id=str(uuid.uuid4()),
        drop_id=drop_id,
        user_id=user_id,
    )
    db.add(sub)
    drop = db.query(DropEvent).filter(DropEvent.drop_id == drop_id).first()
    drop.subscriber_count = (drop.subscriber_count or 0) + 1
    db.commit()
    return sub


def delete_subscription(db, sub: DropSubscription) -> None:
    drop = db.query(DropEvent).filter(DropEvent.drop_id == sub.drop_id).first()
    if drop:
        drop.subscriber_count = max(0, (drop.subscriber_count or 1) - 1)
    db.delete(sub)
    db.commit()


def get_subscriber_user_ids(db, drop_id: str) -> list:
    rows = (
        db.query(DropSubscription.user_id)
        .filter(DropSubscription.drop_id == drop_id)
        .all()
    )
    return [r[0] for r in rows]


def create_notification(db, user_id: str, drop_event, status_label: str) -> None:
    product_name = drop_event.product.product_name if drop_event.product else "상품"
    notif = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=user_id,
        type="drop_status",
        title=f"{product_name} 드랍이 {status_label}되었습니다.",
        target_type="drop",
        target_id=drop_event.drop_id,
        is_read=False,
        send_status="sent",
    )
    db.add(notif)
