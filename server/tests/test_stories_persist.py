"""
test_stories_persist.py — Story 테이블 저장 + 게시·조회·수정·삭제 API
SPEC.md ADR-04 (Feed/Story 저장 구조)
"""
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa
from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, Market, Store, Merchant, Product
from app.db.models.product import StockStatusEnum
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:////tmp/test_stories_persist.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("/tmp/test_stories_persist.db"):
        os.remove("/tmp/test_stories_persist.db")


@pytest.fixture
def db():
    s = TestingSessionLocal()
    yield s
    s.rollback()
    s.close()


@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def seeds():
    s = TestingSessionLocal()
    market_id   = str(uuid.uuid4())
    store_id    = str(uuid.uuid4())
    other_store_id = str(uuid.uuid4())
    merchant_uid   = str(uuid.uuid4())
    other_uid      = str(uuid.uuid4())
    consumer_uid   = str(uuid.uuid4())
    s.add_all([
        Market(market_id=market_id, market_name="저장시장", address="서울", lat=37.5, lng=127.0, zoom=14),
        Store(store_id=store_id, market_id=market_id, store_name="기록상점", zone_label="A"),
        Store(store_id=other_store_id, market_id=market_id, store_name="타인상점", zone_label="B"),
        User(user_id=merchant_uid, email="m1@x.com", password=hash_password("p"), role=RoleEnum.merchant, name="m1"),
        User(user_id=other_uid,    email="m2@x.com", password=hash_password("p"), role=RoleEnum.merchant, name="m2"),
        User(user_id=consumer_uid, email="c1@x.com", password=hash_password("p"), role=RoleEnum.consumer, name="c1"),
        Merchant(merchant_id=str(uuid.uuid4()), store_id=store_id,       user_id=merchant_uid, display_name="m1"),
        Merchant(merchant_id=str(uuid.uuid4()), store_id=other_store_id, user_id=other_uid,    display_name="m2"),
        Product(product_id=str(uuid.uuid4()), store_id=store_id, product_name="감귤",
                price=12000, stock_status=StockStatusEnum.in_stock),
    ])
    s.commit()
    s.close()
    return {
        "market_id":     market_id,
        "store_id":      store_id,
        "other_store_id": other_store_id,
        "merchant_uid":  merchant_uid,
        "other_uid":     other_uid,
        "consumer_uid":  consumer_uid,
    }


@pytest.fixture
def m1_headers(seeds):
    tok = create_access_token({"user_id": seeds["merchant_uid"], "role": "merchant"})
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture
def m2_headers(seeds):
    tok = create_access_token({"user_id": seeds["other_uid"], "role": "merchant"})
    return {"Authorization": f"Bearer {tok}"}


def _create(client, headers, store_id, publish=False):
    return client.post(
        "/api/v1/merchant/stories",
        json={"store_id": store_id, "publish": publish},
        headers=headers,
    )


def test_create_returns_story_id(client, seeds, m1_headers):
    r = _create(client, m1_headers, seeds["store_id"])
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["story_id"]
    assert data["is_published"] is False


def test_create_with_publish_true_marks_published(client, seeds, m1_headers):
    r = _create(client, m1_headers, seeds["store_id"], publish=True)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["is_published"] is True


def test_list_my_stories(client, seeds, m1_headers):
    r = client.get("/api/v1/merchant/stories", headers=m1_headers)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) >= 2  # 위 2건 이상 누적


def test_get_published_for_store_returns_latest(client, seeds, m1_headers):
    _create(client, m1_headers, seeds["store_id"], publish=True)
    r = client.get(f"/api/v1/stores/{seeds['store_id']}/story")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data and data.get("is_published") is True


def test_publish_toggle(client, seeds, m1_headers):
    cr = _create(client, m1_headers, seeds["store_id"], publish=False).json()["data"]
    sid = cr["story_id"]
    r = client.patch(
        f"/api/v1/merchant/stories/{sid}/publish",
        json={"publish": True},
        headers=m1_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["is_published"] is True
    r2 = client.patch(
        f"/api/v1/merchant/stories/{sid}/publish",
        json={"publish": False},
        headers=m1_headers,
    )
    assert r2.json()["data"]["is_published"] is False


def test_other_merchant_cannot_publish(client, seeds, m1_headers, m2_headers):
    cr = _create(client, m1_headers, seeds["store_id"], publish=False).json()["data"]
    sid = cr["story_id"]
    r = client.patch(
        f"/api/v1/merchant/stories/{sid}/publish",
        json={"publish": True},
        headers=m2_headers,
    )
    assert r.status_code == 403


def test_soft_delete(client, seeds, m1_headers):
    cr = _create(client, m1_headers, seeds["store_id"]).json()["data"]
    sid = cr["story_id"]
    r = client.delete(f"/api/v1/merchant/stories/{sid}", headers=m1_headers)
    assert r.status_code == 200
    r2 = client.get(f"/api/v1/merchant/stories/{sid}", headers=m1_headers)
    assert r2.status_code == 404


def test_update_selected_length(client, seeds, m1_headers):
    cr = _create(client, m1_headers, seeds["store_id"]).json()["data"]
    sid = cr["story_id"]
    r = client.patch(
        f"/api/v1/merchant/stories/{sid}",
        json={"selected_length": "detailed", "title": "우리집 감귤 이야기"},
        headers=m1_headers,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["selected_length"] == "detailed"
    assert data["title"] == "우리집 감귤 이야기"


def test_unpublished_store_returns_empty(client, seeds):
    # 게시되지 않은 다른 점포는 빈 응답
    r = client.get(f"/api/v1/stores/{seeds['other_store_id']}/story")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data == {}
