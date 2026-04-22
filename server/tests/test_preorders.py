"""
test_preorders.py — Phase 2-3: Preorder 사용자 플로우 테스트

  - POST /preorders — 주문 생성
  - GET  /preorders — 목록 (consumer/merchant 각각)
  - PATCH /merchant/preorders/{id}/status — 상태 전이 + Notification 생성
  - 권한 검증, 상태 전이 규칙, 409 충돌
"""
import uuid
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa
from app.main import app
from app.db.session import Base, get_db
from app.db.models import (
    User, RoleEnum, Market, Store, Merchant, Notification,
    Preorder, PreorderStatusEnum,
)
from app.db.models.product import StockStatusEnum
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:////tmp/test_preorders.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("/tmp/test_preorders.db"):
        os.remove("/tmp/test_preorders.db")


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
    session = TestingSessionLocal()

    market_id        = str(uuid.uuid4())
    store_id         = str(uuid.uuid4())
    store2_id        = str(uuid.uuid4())   # 다른 점포 (권한 테스트용)
    merchant_user_id = str(uuid.uuid4())
    consumer_user_id = str(uuid.uuid4())
    merchant_id      = str(uuid.uuid4())

    session.add_all([
        Market(market_id=market_id, market_name="사전주문시장", address="서울", lat=37.5, lng=127.0, zoom=14),
        Store(store_id=store_id,  market_id=market_id, store_name="사전주문점포",  zone_label="D구역"),
        Store(store_id=store2_id, market_id=market_id, store_name="다른점포",      zone_label="E구역"),
        User(user_id=merchant_user_id, email="preordermerchant@example.com",
             password=hash_password("test1234"), role=RoleEnum.merchant, name="주문상인"),
        User(user_id=consumer_user_id, email="preorderconsumer@example.com",
             password=hash_password("test1234"), role=RoleEnum.consumer, name="주문소비자"),
        Merchant(merchant_id=merchant_id, store_id=store_id, user_id=merchant_user_id,
                 display_name="사전주문상인"),
    ])
    session.commit()
    session.close()

    return {
        "market_id":        market_id,
        "store_id":         store_id,
        "store2_id":        store2_id,
        "merchant_user_id": merchant_user_id,
        "consumer_user_id": consumer_user_id,
        "merchant_id":      merchant_id,
    }


@pytest.fixture
def merchant_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["merchant_user_id"], "role": "merchant"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def consumer_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["consumer_user_id"], "role": "consumer"})
    return {"Authorization": f"Bearer {token}"}


# ── POST /preorders ────────────────────────────────────────────────────

def test_create_preorder_consumer(client, seed_ids, consumer_headers):
    """소비자가 사전 주문 생성 → 200, preorder_id 반환."""
    resp = client.post(
        "/api/v1/preorders",
        json={"store_id": seed_ids["store_id"], "product_name": "딸기", "qty": 2},
        headers=consumer_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "preorder_id" in data
    assert data["status"] == "requested"
    assert data["product_name"] == "딸기"
    assert data["qty"] == 2


def test_create_preorder_merchant(client, seed_ids, merchant_headers):
    """상인도 사전 주문 생성 가능."""
    resp = client.post(
        "/api/v1/preorders",
        json={"store_id": seed_ids["store_id"], "product_name": "복숭아", "qty": 1},
        headers=merchant_headers,
    )
    assert resp.status_code == 200


def test_create_preorder_invalid_qty(client, seed_ids, consumer_headers):
    """qty < 1 → 422."""
    resp = client.post(
        "/api/v1/preorders",
        json={"store_id": seed_ids["store_id"], "product_name": "수박", "qty": 0},
        headers=consumer_headers,
    )
    assert resp.status_code == 422


def test_create_preorder_unauthenticated(client, seed_ids):
    """인증 없음 → 401."""
    resp = client.post(
        "/api/v1/preorders",
        json={"store_id": seed_ids["store_id"], "product_name": "참외", "qty": 1},
    )
    assert resp.status_code == 401


# ── GET /preorders ─────────────────────────────────────────────────────

def test_list_preorders_consumer(client, consumer_headers):
    """소비자 — 본인 주문만 반환."""
    resp = client.get("/api/v1/preorders", headers=consumer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "pagination" in data
    # 소비자 주문이 최소 1개 이상 (test_create_preorder_consumer 에서 생성)
    assert data["pagination"]["total"] >= 1
    for item in data["items"]:
        assert item["status"] in ("requested", "confirmed", "ready", "cancelled")


def test_list_preorders_merchant(client, merchant_headers):
    """상인 — 담당 점포 주문 전체 반환."""
    resp = client.get("/api/v1/preorders", headers=merchant_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["pagination"]["total"] >= 1


def test_list_preorders_pagination(client, seed_ids, consumer_headers):
    """페이지네이션 파라미터 동작."""
    resp = client.get("/api/v1/preorders?page=1&size=1", headers=consumer_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) <= 1
    assert "has_next" in data["pagination"]


# ── PATCH /merchant/preorders/{id}/status ──────────────────────────────

def _get_first_consumer_preorder_id(client, consumer_headers) -> str:
    resp = client.get("/api/v1/preorders", headers=consumer_headers)
    items = resp.json()["data"]["items"]
    # requested 상태인 첫 번째 주문 반환
    for item in items:
        if item["status"] == "requested":
            return item["preorder_id"]
    return items[0]["preorder_id"]


def test_update_status_requested_to_confirmed(client, db, seed_ids, merchant_headers, consumer_headers):
    """requested → confirmed: 200, Notification 생성."""
    preorder_id = _get_first_consumer_preorder_id(client, consumer_headers)

    before_count = (
        db.query(Notification)
        .filter(Notification.target_id == preorder_id)
        .count()
    )

    resp = client.patch(
        f"/api/v1/merchant/preorders/{preorder_id}/status",
        json={"status": "confirmed"},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "confirmed"

    db.expire_all()
    after_count = (
        db.query(Notification)
        .filter(Notification.target_id == preorder_id)
        .count()
    )
    assert after_count >= before_count + 1


def test_update_status_confirmed_to_ready(client, seed_ids, merchant_headers, consumer_headers):
    """confirmed → ready: 200."""
    # confirmed 상태인 주문 찾기
    resp = client.get("/api/v1/preorders", headers=consumer_headers)
    items = resp.json()["data"]["items"]
    confirmed = next((i for i in items if i["status"] == "confirmed"), None)
    if not confirmed:
        pytest.skip("confirmed 주문 없음 — 순서 의존성")

    resp = client.patch(
        f"/api/v1/merchant/preorders/{confirmed['preorder_id']}/status",
        json={"status": "ready"},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ready"


def test_update_status_invalid_transition(client, db, seed_ids, merchant_headers, consumer_headers):
    """유효하지 않은 전이 (requested → ready) → 409."""
    # 새 주문 직접 생성
    session = TestingSessionLocal()
    po = Preorder(
        preorder_id  = str(uuid.uuid4()),
        user_id      = seed_ids["consumer_user_id"],
        store_id     = seed_ids["store_id"],
        product_name = "전이테스트상품",
        qty          = 1,
        status       = PreorderStatusEnum.requested,
    )
    session.add(po)
    session.commit()
    preorder_id = po.preorder_id
    session.close()

    resp = client.patch(
        f"/api/v1/merchant/preorders/{preorder_id}/status",
        json={"status": "ready"},  # requested → ready 불가
        headers=merchant_headers,
    )
    assert resp.status_code == 409


def test_update_status_not_found(client, merchant_headers):
    """존재하지 않는 preorder_id → 404."""
    resp = client.patch(
        "/api/v1/merchant/preorders/no-such-id/status",
        json={"status": "confirmed"},
        headers=merchant_headers,
    )
    assert resp.status_code == 404


def test_update_status_consumer_forbidden(client, seed_ids, consumer_headers, db):
    """소비자는 상태 변경 불가 → 403."""
    po = Preorder(
        preorder_id  = str(uuid.uuid4()),
        user_id      = seed_ids["consumer_user_id"],
        store_id     = seed_ids["store_id"],
        product_name = "소비자변경시도",
        qty          = 1,
        status       = PreorderStatusEnum.requested,
    )
    session = TestingSessionLocal()
    session.add(po)
    session.commit()
    preorder_id = po.preorder_id
    session.close()

    resp = client.patch(
        f"/api/v1/merchant/preorders/{preorder_id}/status",
        json={"status": "confirmed"},
        headers=consumer_headers,
    )
    assert resp.status_code == 403


def test_update_status_wrong_store(client, seed_ids, db):
    """다른 점포 주문을 변경 시도 → 403."""
    # 두 번째 점포의 상인 (별도 상인)
    user2_id   = str(uuid.uuid4())
    merch2_id  = str(uuid.uuid4())

    session = TestingSessionLocal()
    session.add_all([
        User(user_id=user2_id, email="merchant2@example.com",
             password=hash_password("test1234"), role=RoleEnum.merchant, name="상인2"),
        Merchant(merchant_id=merch2_id, store_id=seed_ids["store2_id"], user_id=user2_id,
                 display_name="다른상인"),
    ])

    # store2_id 주문 생성
    po = Preorder(
        preorder_id  = str(uuid.uuid4()),
        user_id      = seed_ids["consumer_user_id"],
        store_id     = seed_ids["store2_id"],
        product_name = "다른점포상품",
        qty          = 1,
        status       = PreorderStatusEnum.requested,
    )
    session.add(po)
    session.commit()
    preorder_id = po.preorder_id
    session.close()

    # 원래 merchant (store_id 담당)가 store2_id 주문 변경 시도
    resp = client.patch(
        f"/api/v1/merchant/preorders/{preorder_id}/status",
        json={"status": "confirmed"},
        # merchant_headers fixture 대신 직접 생성
        headers={"Authorization": f"Bearer {create_access_token({'user_id': seed_ids['merchant_user_id'], 'role': 'merchant'})}"},
    )
    assert resp.status_code == 403


def test_update_status_notification_content(client, db, seed_ids, merchant_headers, consumer_headers):
    """Notification의 target_type='preorder', target_id=preorder_id 확인."""
    # 새 requested 주문 생성
    session = TestingSessionLocal()
    po = Preorder(
        preorder_id  = str(uuid.uuid4()),
        user_id      = seed_ids["consumer_user_id"],
        store_id     = seed_ids["store_id"],
        product_name = "알림확인상품",
        qty          = 3,
        status       = PreorderStatusEnum.requested,
    )
    session.add(po)
    session.commit()
    preorder_id = po.preorder_id
    session.close()

    client.patch(
        f"/api/v1/merchant/preorders/{preorder_id}/status",
        json={"status": "confirmed"},
        headers=merchant_headers,
    )

    db.expire_all()
    notif = (
        db.query(Notification)
        .filter(
            Notification.target_id   == preorder_id,
            Notification.target_type == "preorder",
        )
        .first()
    )
    assert notif is not None
    assert notif.user_id == seed_ids["consumer_user_id"]
    assert "알림확인상품" in notif.body
