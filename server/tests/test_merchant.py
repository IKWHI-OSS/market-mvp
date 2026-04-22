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
    User, RoleEnum, DropEvent, DropSubscription, Market, Store, Merchant, Product, Notification
)
from app.db.models.drop_event import DropStatusEnum
from app.db.models.product import StockStatusEnum
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test_merchant.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_merchant.db"):
        os.remove("test_merchant.db")


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
    """Create Market, Store, Merchant, Users, Product, DropEvent once for the module."""
    session = TestingSessionLocal()

    market_id = str(uuid.uuid4())
    store_id = str(uuid.uuid4())
    merchant_user_id = str(uuid.uuid4())
    consumer_user_id = str(uuid.uuid4())
    merchant_id = str(uuid.uuid4())
    product_id = str(uuid.uuid4())
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
        store_name="테스트 과일나라",
        zone_label="A구역",
    )
    merchant_user = User(
        user_id=merchant_user_id,
        email="merchant@example.com",
        password=hash_password("test1234"),
        role=RoleEnum.merchant,
        name="상인유저",
    )
    consumer_user = User(
        user_id=consumer_user_id,
        email="consumer@example.com",
        password=hash_password("test1234"),
        role=RoleEnum.consumer,
        name="소비자유저",
    )
    merchant = Merchant(
        merchant_id=merchant_id,
        store_id=store_id,
        user_id=merchant_user_id,
        display_name="테스트상인",
    )
    product = Product(
        product_id=product_id,
        store_id=store_id,
        product_name="사과",
        price=3000,
        stock_status=StockStatusEnum.low_stock,
    )
    drop = DropEvent(
        drop_id=drop_id,
        product_id=product_id,
        store_id=store_id,
        title="사과 드랍",
        expected_at=datetime(2026, 4, 21, 8, 0, 0),
        status=DropStatusEnum.scheduled,
        subscriber_count=0,
    )

    session.add_all([market, store, merchant_user, consumer_user, merchant, product, drop])
    session.commit()
    session.close()

    return {
        "market_id": market_id,
        "store_id": store_id,
        "merchant_user_id": merchant_user_id,
        "consumer_user_id": consumer_user_id,
        "merchant_id": merchant_id,
        "product_id": product_id,
        "drop_id": drop_id,
    }


@pytest.fixture
def merchant_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["merchant_user_id"], "role": "merchant"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def consumer_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["consumer_user_id"], "role": "consumer"})
    return {"Authorization": f"Bearer {token}"}


# Test 1: GET /merchant/dashboard with merchant token → 200, has all 4 fields
def test_dashboard_merchant(client, seed_ids, merchant_headers):
    resp = client.get("/api/v1/merchant/dashboard", headers=merchant_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "today_product_count" in data
    assert "risk_stock_count" in data
    assert "pending_request_count" in data
    assert "today_drop_count" in data
    assert data["pending_request_count"] == 0
    assert data["today_product_count"] >= 1
    assert data["risk_stock_count"] >= 1
    assert data["today_drop_count"] >= 1


# Test 2: GET /merchant/dashboard with consumer token → 403
def test_dashboard_consumer_forbidden(client, consumer_headers):
    resp = client.get("/api/v1/merchant/dashboard", headers=consumer_headers)
    assert resp.status_code == 403


# Test 3: POST /merchant/products with valid data → 200, product_id in response
def test_create_product_valid(client, seed_ids, merchant_headers):
    resp = client.post(
        "/api/v1/merchant/products",
        json={
            "store_id": seed_ids["store_id"],
            "product_name": "배",
            "price": 5000,
            "stock_status": "in_stock",
            "category": "과일",
        },
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "product_id" in data
    assert data["product_name"] == "배"
    assert data["price"] == 5000
    assert data["stock_status"] == "in_stock"
    assert data["store_id"] == seed_ids["store_id"]


# Test 4: POST /merchant/products missing product_name → 422
def test_create_product_missing_name(client, seed_ids, merchant_headers):
    resp = client.post(
        "/api/v1/merchant/products",
        json={
            "store_id": seed_ids["store_id"],
            "price": 5000,
            "stock_status": "in_stock",
        },
        headers=merchant_headers,
    )
    assert resp.status_code == 422


# Test 5: POST /merchant/products with consumer token → 403
def test_create_product_consumer_forbidden(client, seed_ids, consumer_headers):
    resp = client.post(
        "/api/v1/merchant/products",
        json={
            "store_id": seed_ids["store_id"],
            "product_name": "배",
            "price": 5000,
            "stock_status": "in_stock",
        },
        headers=consumer_headers,
    )
    assert resp.status_code == 403


# Test 6: POST /merchant/products/ai-draft → 200, fallback_mode=false, draft has expected keys
def test_ai_draft_success(client, seed_ids, merchant_headers):
    resp = client.post(
        "/api/v1/merchant/products/ai-draft",
        json={"store_id": seed_ids["store_id"]},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["fallback_mode"] is False
    assert "draft" in data
    draft = data["draft"]
    assert "product_name" in draft
    assert "category" in draft
    assert "description" in draft


# Test 7: POST /merchant/products/ai-draft with ai_fn that raises exception → fallback_mode=true, HTTP 200
def test_ai_draft_fallback(db):
    from app.db.models.user import RoleEnum

    class FakeUser:
        user_id = "fake"
        role = type('R', (), {'value': 'merchant'})()

    from app.services import merchant_service
    result = merchant_service.ai_draft(
        db,
        FakeUser(),
        "store_x",
        ai_fn=lambda **kw: (_ for _ in ()).throw(RuntimeError("AI error")),
    )
    assert result["fallback_mode"] is True
    assert result["draft"] == {}


# Test 8: PATCH /merchant/drops/{drop_id}/status → 200, status updated
def test_update_drop_status(client, db, seed_ids, merchant_headers):
    resp = client.patch(
        f"/api/v1/merchant/drops/{seed_ids['drop_id']}/status",
        json={"status": "arrived"},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["drop_id"] == seed_ids["drop_id"]
    assert data["status"] == "arrived"

    # Verify in DB
    db.expire_all()
    drop = db.query(DropEvent).filter(DropEvent.drop_id == seed_ids["drop_id"]).first()
    assert drop.status.value == "arrived"

    # Reset status back to scheduled for subsequent tests
    drop.status = DropStatusEnum.scheduled
    db.commit()


# Test 9: PATCH /merchant/drops/{drop_id}/status same status → 409
def test_update_drop_status_conflict(client, seed_ids, merchant_headers):
    # Current status is scheduled (reset in test 8)
    resp = client.patch(
        f"/api/v1/merchant/drops/{seed_ids['drop_id']}/status",
        json={"status": "scheduled"},
        headers=merchant_headers,
    )
    assert resp.status_code == 409


# Test 10: PATCH /merchant/drops/unknown/status → 404
def test_update_drop_status_not_found(client, merchant_headers):
    resp = client.patch(
        "/api/v1/merchant/drops/unknown-drop-id/status",
        json={"status": "arrived"},
        headers=merchant_headers,
    )
    assert resp.status_code == 404


# Test 11: PATCH /merchant/drops/{drop_id}/status with consumer token → 403
def test_update_drop_status_consumer_forbidden(client, seed_ids, consumer_headers):
    resp = client.patch(
        f"/api/v1/merchant/drops/{seed_ids['drop_id']}/status",
        json={"status": "arrived"},
        headers=consumer_headers,
    )
    assert resp.status_code == 403


# Test 12: PATCH /merchant/drops/{drop_id}/status → Notification created for subscribers
def test_update_drop_status_creates_notification(client, db, seed_ids, merchant_headers):
    # Create a subscription for the consumer
    sub = DropSubscription(
        subscription_id=str(uuid.uuid4()),
        drop_id=seed_ids["drop_id"],
        user_id=seed_ids["consumer_user_id"],
    )
    db.add(sub)
    db.commit()

    before_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == seed_ids["consumer_user_id"],
            Notification.target_id == seed_ids["drop_id"],
        )
        .count()
    )

    resp = client.patch(
        f"/api/v1/merchant/drops/{seed_ids['drop_id']}/status",
        json={"status": "arrived"},
        headers=merchant_headers,
    )
    assert resp.status_code == 200

    db.expire_all()
    after_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == seed_ids["consumer_user_id"],
            Notification.target_id == seed_ids["drop_id"],
        )
        .count()
    )
    assert after_count >= before_count + 1

    # Clean up
    db.query(DropSubscription).filter(
        DropSubscription.subscription_id == sub.subscription_id
    ).delete()
    db.commit()
