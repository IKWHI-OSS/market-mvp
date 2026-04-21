import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # registers all models — MUST come before `from app.main import app`

from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, Product, StockStatusEnum, Store, Market

TEST_DB_URL = "sqlite:///./test_products.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_products.db"):
        os.remove("test_products.db")


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
def seed_data():
    """Create Market, Store, and two Products once for the module."""
    session = TestingSessionLocal()
    market_id = str(uuid.uuid4())
    store_id = str(uuid.uuid4())
    product1_id = str(uuid.uuid4())
    product2_id = str(uuid.uuid4())

    market = Market(
        market_id=market_id,
        market_name="테스트시장",
        address="서울시 테스트구 1",
        lat=37.5,
        lng=127.0,
        zoom=15,
    )
    store = Store(
        store_id=store_id,
        market_id=market_id,
        store_name="테스트점포",
        zone_label="A구역",
    )
    product1 = Product(
        product_id=product1_id,
        store_id=store_id,
        product_name="사과",
        category="과일",
        price=1000,
        stock_status=StockStatusEnum.in_stock,
    )
    product2 = Product(
        product_id=product2_id,
        store_id=store_id,
        product_name="배",
        category="과일",
        price=2000,
        stock_status=StockStatusEnum.out_of_stock,
    )

    session.add_all([market, store, product1, product2])
    session.commit()
    session.close()

    yield {
        "market_id": market_id,
        "store_id": store_id,
        "product1_id": product1_id,
        "product2_id": product2_id,
    }


def test_search_returns_items_and_pagination(client, seed_data):
    resp = client.get("/api/v1/products/search", params={"q": "사과"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) >= 1
    assert data["pagination"]["total"] >= 1
    item = data["items"][0]
    assert item["product_name"] == "사과"
    assert item["store_name"] == "테스트점포"
    assert item["zone_label"] == "A구역"


def test_search_no_results(client, seed_data):
    resp = client.get("/api/v1/products/search", params={"q": "없는상품xyz"})
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert data["items"] == []
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["has_next"] is False


def test_search_with_stock_status_filter(client, seed_data):
    resp = client.get(
        "/api/v1/products/search",
        params={"q": "배", "stock_status": "out_of_stock"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["pagination"]["total"] >= 1
    for item in data["items"]:
        assert item["stock_status"] == "out_of_stock"


def test_search_with_sort_price_asc(client, seed_data):
    resp = client.get(
        "/api/v1/products/search",
        params={"q": "아", "sort": "price_asc"},  # partial match for 사과/배 won't work; use broad q
    )
    # Use a broad query that matches both products
    resp = client.get(
        "/api/v1/products/search",
        params={"q": "", "sort": "price_asc"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    items = data["items"]
    if len(items) >= 2:
        prices = [item["price"] for item in items]
        assert prices == sorted(prices)


def test_get_product_detail(client, seed_data):
    product_id = seed_data["product1_id"]
    resp = client.get(f"/api/v1/products/{product_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["product_id"] == product_id
    assert data["product_name"] == "사과"
    assert data["stock_status"] == "in_stock"
    assert "store" in data
    assert data["store"]["zone_label"] == "A구역"
    assert data["store"]["store_name"] == "테스트점포"


def test_get_product_not_found(client, seed_data):
    resp = client.get("/api/v1/products/unknown-id-does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
