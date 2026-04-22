import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # ensures all models are registered with Base.metadata

from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, Notification
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test_notifications.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_notifications.db"):
        os.remove("test_notifications.db")


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


@pytest.fixture
def test_user(db):
    user = User(
        user_id=str(uuid.uuid4()),
        email="consumer@test.com",
        password=hash_password("password123"),
        role=RoleEnum.consumer,
        name="테스트소비자",
    )
    db.add(user)
    db.commit()
    yield user
    db.query(User).filter(User.email == "consumer@test.com").delete()
    db.commit()


@pytest.fixture
def test_token(test_user):
    return create_access_token({"user_id": test_user.user_id, "role": "consumer"})


@pytest.fixture
def test_notifications(db, test_user):
    notif1 = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=test_user.user_id,
        type="drop_status",
        title="단감 드랍이 도착되었습니다.",
        body=None,
        target_type="drop",
        target_id="drop_001",
        is_read=False,
    )
    notif2 = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=test_user.user_id,
        type="event_info",
        title="새로운 행사가 있습니다.",
        body=None,
        target_type="event",
        target_id="event_001",
        is_read=True,
    )
    db.add(notif1)
    db.add(notif2)
    db.commit()
    yield [notif1, notif2]


def test_list_notifications_with_valid_token(client, test_user, test_token, test_notifications):
    """GET /api/v1/notifications with valid token — returns items + pagination"""
    resp = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {test_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "pagination" in body["data"]
    assert len(body["data"]["items"]) == 2
    assert body["data"]["pagination"]["total"] == 2
    assert body["data"]["pagination"]["page"] == 1
    assert body["data"]["pagination"]["size"] == 20
    assert body["data"]["pagination"]["has_next"] is False


def test_list_notifications_unread_filter(client, test_user, test_token, test_notifications):
    """GET /api/v1/notifications?is_read=0 — returns only unread"""
    resp = client.get("/api/v1/notifications?is_read=0", headers={"Authorization": f"Bearer {test_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["is_read"] is False
    assert body["data"]["pagination"]["total"] == 1


def test_list_notifications_read_filter(client, test_user, test_token, test_notifications):
    """GET /api/v1/notifications?is_read=1 — returns only read"""
    resp = client.get("/api/v1/notifications?is_read=1", headers={"Authorization": f"Bearer {test_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["is_read"] is True
    assert body["data"]["pagination"]["total"] == 1


def test_list_notifications_without_token(client):
    """GET /api/v1/notifications without token — 401"""
    resp = client.get("/api/v1/notifications")
    assert resp.status_code == 403


def test_mark_notification_read(client, test_user, test_token, test_notifications):
    """PATCH /api/v1/notifications/{id}/read — marks as read, returns is_read=true"""
    notif_id = test_notifications[0].notification_id
    resp = client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["notification_id"] == notif_id
    assert body["data"]["is_read"] is True


def test_mark_notification_read_unknown_id(client, test_user, test_token):
    """PATCH /api/v1/notifications/unknown-id/read — 404"""
    resp = client.patch(
        "/api/v1/notifications/unknown-id-12345/read",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert resp.status_code == 404
