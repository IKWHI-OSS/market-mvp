"""
test_prices.py — Phase 2-1: 가격/재고 고도화 테스트
  - MarketPrice upsert
  - ProductPriceHistory 기록
  - KAMIS sync (fallback 포함)
  - 상품 가격 자동 업데이트 API
  - 가격 이력 조회 API
  - 가격 정책 보조 문구 API
"""
import uuid
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401 — model registry
from app.main import app
from app.db.session import Base, get_db
from app.db.models import (
    User, RoleEnum, Market, Store, Merchant, Product,
    MarketPrice, ProductPriceHistory, PriceChangeReasonEnum,
)
from app.db.models.product import StockStatusEnum
from app.core.security import hash_password, create_access_token
from app.db.repositories.price_repository import (
    upsert_market_price, record_price_change, get_latest_market_price, get_price_history,
)

import datetime

TEST_DB_URL = "sqlite:////tmp/test_prices.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("/tmp/test_prices.db"):
        os.remove("/tmp/test_prices.db")


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

    market_id         = str(uuid.uuid4())
    store_id          = str(uuid.uuid4())
    merchant_user_id  = str(uuid.uuid4())
    consumer_user_id  = str(uuid.uuid4())
    merchant_id       = str(uuid.uuid4())
    product_id        = str(uuid.uuid4())

    session.add_all([
        Market(market_id=market_id, market_name="가격테스트시장", address="서울", lat=37.5, lng=127.0, zoom=14),
        Store(store_id=store_id, market_id=market_id, store_name="가격테스트점포", zone_label="B구역"),
        User(user_id=merchant_user_id, email="pricemerchant@example.com",
             password=hash_password("test1234"), role=RoleEnum.merchant, name="가격상인"),
        User(user_id=consumer_user_id, email="priceconsumer@example.com",
             password=hash_password("test1234"), role=RoleEnum.consumer, name="가격소비자"),
        Merchant(merchant_id=merchant_id, store_id=store_id, user_id=merchant_user_id,
                 display_name="가격테스트상인"),
        Product(product_id=product_id, store_id=store_id, product_name="사과",
                price=5000, stock_status=StockStatusEnum.in_stock),
    ])
    session.commit()
    session.close()

    return {
        "market_id": market_id,
        "store_id": store_id,
        "merchant_user_id": merchant_user_id,
        "consumer_user_id": consumer_user_id,
        "merchant_id": merchant_id,
        "product_id": product_id,
    }


@pytest.fixture
def merchant_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["merchant_user_id"], "role": "merchant"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def consumer_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["consumer_user_id"], "role": "consumer"})
    return {"Authorization": f"Bearer {token}"}


# ── 레포지토리 단위 테스트 ────────────────────────────────────────────

def test_upsert_market_price_create(db):
    """새 MarketPrice 생성."""
    mp = upsert_market_price(
        db,
        item_name="사과/후지",
        kamis_item_code="214",
        unit="10개",
        price_date=datetime.date(2026, 4, 1),
        retail_price=15000,
        prev_day_price=14800,
    )
    assert mp.market_price_id is not None
    assert mp.retail_price == 15000
    assert mp.kamis_item_code == "214"


def test_upsert_market_price_update(db):
    """동일 (code, name, date) → 가격 업데이트."""
    upsert_market_price(
        db,
        item_name="사과/후지",
        kamis_item_code="214",
        unit="10개",
        price_date=datetime.date(2026, 4, 1),
        retail_price=15500,
    )
    mp = get_latest_market_price(db, "214")
    assert mp.retail_price == 15500


def test_record_price_change(db, seed_ids):
    """ProductPriceHistory 기록."""
    h = record_price_change(
        db,
        product_id=seed_ids["product_id"],
        old_price=5000,
        new_price=6000,
        reason=PriceChangeReasonEnum.kamis,
    )
    assert h.history_id is not None
    assert h.reason == PriceChangeReasonEnum.kamis
    assert h.new_price == 6000


def test_get_price_history_list(db, seed_ids):
    """이력 목록 조회."""
    histories = get_price_history(db, seed_ids["product_id"])
    assert len(histories) >= 1


# ── API 테스트 ────────────────────────────────────────────────────────

def test_get_market_price_not_found(client):
    """저장된 시세 없을 때 404."""
    resp = client.get("/api/v1/prices/market/999")
    assert resp.status_code == 404


def test_get_market_price_found(client, db):
    """저장된 시세 있을 때 200."""
    upsert_market_price(
        db,
        item_name="감/단감",
        kamis_item_code="421",
        unit="10개",
        price_date=datetime.date.today(),
        retail_price=20000,
    )
    resp = client.get("/api/v1/prices/market/421")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["kamis_item_code"] == "421"
    assert body["data"]["retail_price"] == 20000


def test_sync_market_price_fallback(client, merchant_headers):
    """KAMIS_API_KEY 없을 때 fallback → DB에 기존 값 없으면 404 or fallback_mode=True."""
    # KAMIS_API_KEY 미설정 상태 (test 환경)
    resp = client.post("/api/v1/prices/market/214/sync", headers=merchant_headers)
    # DB에 이미 214 데이터 있으므로 fallback_mode=True, 200
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["fallback_mode"] is True


def test_update_product_price_no_market_data(client, seed_ids, merchant_headers):
    """시세 데이터 없는 품목코드 → 400."""
    resp = client.post(
        f"/api/v1/merchant/products/{seed_ids['product_id']}/price",
        params={"kamis_item_code": "999"},
        headers=merchant_headers,
    )
    assert resp.status_code == 400


def test_update_product_price_ok(client, db, seed_ids, merchant_headers):
    """시세 데이터 있는 경우 가격 자동 업데이트."""
    # 사전에 214 시세 저장 (이미 test_sync에서 저장됨)
    resp = client.post(
        f"/api/v1/merchant/products/{seed_ids['product_id']}/price",
        params={"kamis_item_code": "214"},
        headers=merchant_headers,
    )
    # retail_price=15500 이 저장되어 있으므로 성공
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["product_id"] == seed_ids["product_id"]
    assert data["new_price"] == 15500


def test_update_product_price_consumer_forbidden(client, seed_ids, consumer_headers):
    """소비자 권한 → 403."""
    resp = client.post(
        f"/api/v1/merchant/products/{seed_ids['product_id']}/price",
        params={"kamis_item_code": "214"},
        headers=consumer_headers,
    )
    assert resp.status_code == 403


def test_get_price_history_api(client, seed_ids, merchant_headers):
    """가격 이력 조회 API."""
    resp = client.get(
        f"/api/v1/merchant/products/{seed_ids['product_id']}/price-history",
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    items = body["data"]["items"]
    assert len(items) >= 1
    assert "old_price" in items[0]
    assert "new_price" in items[0]
    assert "reason" in items[0]


def test_price_suggestions_api(client, merchant_headers):
    """가격 정책 보조 문구 API — 결과 리스트 반환."""
    resp = client.get(
        "/api/v1/merchant/dashboard/price-suggestions",
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "suggestions" in body["data"]


def test_price_suggestions_consumer_forbidden(client, consumer_headers):
    """소비자는 가격 정책 보조 조회 불가 → 403."""
    resp = client.get(
        "/api/v1/merchant/dashboard/price-suggestions",
        headers=consumer_headers,
    )
    assert resp.status_code == 403
