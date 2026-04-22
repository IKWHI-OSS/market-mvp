import uuid
import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # MUST come before "from app.main import app"
from app.main import app
from app.db.session import Base, get_db
from app.db.models import (
    User, RoleEnum, DropEvent, DropSubscription, Market, Store, Product, Notification
)
from app.db.models.drop_event import DropStatusEnum
from app.core.security import hash_password, create_access_token
from app.services import drop_service

TEST_DB_URL = "sqlite:///./test_drops.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_drops.db"):
        os.remove("test_drops.db")


@pytest.fixture
def db():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def seed_ids():
    """Create Market, Store, Product, User, DropEvent once for the module."""
    session = TestingSessionLocal()

    market_id = str(uuid.uuid4())
    store_id = str(uuid.uuid4())
    product_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    drop_id = str(uuid.uuid4())

    market = Market(
        market_id=market_id,
        market_name="테스트시장",
        address="서울시 테스트구 1",
        lat=37.5,
        lng=127.0,
        zoom=14,
    )
    store = Store(
        store_id=store_id,
        market_id=market_id,
        store_name="망원 과일나라",
        zone_label="A구역",
    )
    product = Product(
        product_id=product_id,
        store_id=store_id,
        product_name="단감",
        price=3000,
    )
    user = User(
        user_id=user_id,
        email="drop_test@example.com",
        password=hash_password("test1234"),
        role=RoleEnum.consumer,
        name="테스트유저",
    )
    drop = DropEvent(
        drop_id=drop_id,
        product_id=product_id,
        store_id=store_id,
        title="단감 드랍",
        expected_at=datetime(2026, 4, 21, 8, 0, 0),
        status=DropStatusEnum.scheduled,
        subscriber_count=0,
    )

    session.add_all([market, store, product, user, drop])
    session.commit()
    session.close()

    return {
        "market_id": market_id,
        "store_id": store_id,
        "product_id": product_id,
        "user_id": user_id,
        "drop_id": drop_id,
    }


# Test 1: GET /api/v1/drops — returns items with pagination (no auth)
def test_list_drops_no_auth(client, seed_ids):
    resp = client.get("/api/v1/drops")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) >= 1
    item = data["items"][0]
    assert item["drop_id"] == seed_ids["drop_id"]
    assert item["product_name"] == "단감"
    assert item["store_name"] == "망원 과일나라"
    assert item["is_subscribed"] is False
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["size"] == 20


# Test 2: GET /api/v1/drops?status=scheduled — filters by status
def test_list_drops_filter_by_status(client, seed_ids):
    resp = client.get("/api/v1/drops?status=scheduled")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert item["status"] == "scheduled"

    # Filter by non-matching status should return 0
    resp2 = client.get("/api/v1/drops?status=arrived")
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert data2["pagination"]["total"] == 0


# Test 3: GET /api/v1/drops with valid Bearer token — is_subscribed=True for subscribed drop
def test_list_drops_with_auth_is_subscribed(client, db, seed_ids):
    # Create a subscription directly
    sub = DropSubscription(
        subscription_id=str(uuid.uuid4()),
        drop_id=seed_ids["drop_id"],
        user_id=seed_ids["user_id"],
    )
    db.add(sub)
    db.commit()

    token = create_access_token({"user_id": seed_ids["user_id"], "role": "consumer"})
    resp = client.get(
        "/api/v1/drops",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    drop_item = next(
        (i for i in data["items"] if i["drop_id"] == seed_ids["drop_id"]), None
    )
    assert drop_item is not None
    assert drop_item["is_subscribed"] is True

    # Clean up subscription so other tests start fresh
    db.delete(sub)
    db.commit()


# Test 4: POST /api/v1/drops/{drop_id}/subscribe with valid token — 200, subscribed=True
def test_subscribe_drop(client, db, seed_ids):
    token = create_access_token({"user_id": seed_ids["user_id"], "role": "consumer"})
    resp = client.post(
        f"/api/v1/drops/{seed_ids['drop_id']}/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["subscribed"] is True
    assert body["data"]["drop_id"] == seed_ids["drop_id"]

    # Verify subscriber_count incremented
    db.expire_all()
    drop = db.query(DropEvent).filter(DropEvent.drop_id == seed_ids["drop_id"]).first()
    assert drop.subscriber_count >= 1


# Test 5: POST /api/v1/drops/{drop_id}/subscribe again — 409 conflict
def test_subscribe_drop_conflict(client, seed_ids):
    token = create_access_token({"user_id": seed_ids["user_id"], "role": "consumer"})
    # Already subscribed from test 4
    resp = client.post(
        f"/api/v1/drops/{seed_ids['drop_id']}/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409


# Test 6: DELETE /api/v1/drops/{drop_id}/subscribe with valid token — 200, subscribed=False
def test_unsubscribe_drop(client, db, seed_ids):
    token = create_access_token({"user_id": seed_ids["user_id"], "role": "consumer"})
    resp = client.delete(
        f"/api/v1/drops/{seed_ids['drop_id']}/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["subscribed"] is False
    assert body["data"]["drop_id"] == seed_ids["drop_id"]

    # Verify subscriber_count decremented
    db.expire_all()
    drop = db.query(DropEvent).filter(DropEvent.drop_id == seed_ids["drop_id"]).first()
    assert drop.subscriber_count == 0


# Test 7: POST /api/v1/drops/unknown/subscribe — 404
def test_subscribe_unknown_drop(client, seed_ids):
    token = create_access_token({"user_id": seed_ids["user_id"], "role": "consumer"})
    resp = client.post(
        "/api/v1/drops/unknown-drop-id/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# Test 8: trigger_drop_status_notifications creates Notification rows for subscribers
def test_trigger_drop_status_notifications(db, seed_ids):
    # Create a subscription for the user
    sub = DropSubscription(
        subscription_id=str(uuid.uuid4()),
        drop_id=seed_ids["drop_id"],
        user_id=seed_ids["user_id"],
    )
    db.add(sub)
    db.commit()

    drop = db.query(DropEvent).filter(DropEvent.drop_id == seed_ids["drop_id"]).first()
    drop.status = DropStatusEnum.arrived
    db.commit()
    db.refresh(drop)

    # Count existing notifications before
    before_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == seed_ids["user_id"],
            Notification.target_id == seed_ids["drop_id"],
        )
        .count()
    )

    drop_service.trigger_drop_status_notifications(db, drop)

    after_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == seed_ids["user_id"],
            Notification.target_id == seed_ids["drop_id"],
        )
        .count()
    )
    assert after_count == before_count + 1

    notif = (
        db.query(Notification)
        .filter(
            Notification.user_id == seed_ids["user_id"],
            Notification.target_id == seed_ids["drop_id"],
        )
        .order_by(Notification.notification_id.desc())
        .first()
    )
    assert notif is not None
    assert notif.type == "drop_status"
    assert "도착" in notif.title
    assert notif.target_type == "drop"
    assert notif.send_status == "sent"
    assert notif.is_read is False

    # Clean up
    db.delete(sub)
    db.delete(notif)
    db.commit()
