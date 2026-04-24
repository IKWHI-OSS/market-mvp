import uuid
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401 — registers all models before app init
from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, Market, Store, Merchant, Product
from app.db.models.product import StockStatusEnum
from app.db.models.market_price import ProductPriceHistory
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:////tmp/test_merchant_price.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("/tmp/test_merchant_price.db"):
        os.remove("/tmp/test_merchant_price.db")


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

    market_id = str(uuid.uuid4())
    store_id = str(uuid.uuid4())
    other_store_id = str(uuid.uuid4())
    merchant_user_id = str(uuid.uuid4())
    other_merchant_user_id = str(uuid.uuid4())
    product_id = str(uuid.uuid4())
    other_product_id = str(uuid.uuid4())

    market = Market(market_id=market_id, market_name="가격테스트시장", address="서울시 테스트구", lat=37.5, lng=127.0, zoom=14)
    store = Store(store_id=store_id, market_id=market_id, store_name="가격테스트점포", zone_label="A구역")
    other_store = Store(store_id=other_store_id, market_id=market_id, store_name="타상인점포", zone_label="B구역")

    merchant_user = User(user_id=merchant_user_id, email="pricemerchant@example.com",
                         password=hash_password("test1234"), role=RoleEnum.merchant, name="가격상인")
    other_merchant_user = User(user_id=other_merchant_user_id, email="othermerchant@example.com",
                               password=hash_password("test1234"), role=RoleEnum.merchant, name="타상인")

    merchant = Merchant(merchant_id=str(uuid.uuid4()), store_id=store_id, user_id=merchant_user_id, display_name="가격상인")
    other_merchant = Merchant(merchant_id=str(uuid.uuid4()), store_id=other_store_id, user_id=other_merchant_user_id, display_name="타상인")

    product = Product(product_id=product_id, store_id=store_id, product_name="배추",
                      price=3000, stock_status=StockStatusEnum.in_stock)
    other_product = Product(product_id=other_product_id, store_id=other_store_id,
                            product_name="무", price=2000, stock_status=StockStatusEnum.in_stock)

    session.add_all([market, store, other_store, merchant_user, other_merchant_user,
                     merchant, other_merchant, product, other_product])
    session.commit()
    session.close()

    return {
        "store_id": store_id,
        "other_store_id": other_store_id,
        "merchant_user_id": merchant_user_id,
        "other_merchant_user_id": other_merchant_user_id,
        "product_id": product_id,
        "other_product_id": other_product_id,
    }


@pytest.fixture
def merchant_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["merchant_user_id"], "role": "merchant"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_merchant_headers(seed_ids):
    token = create_access_token({"user_id": seed_ids["other_merchant_user_id"], "role": "merchant"})
    return {"Authorization": f"Bearer {token}"}


def test_patch_price_changes_price(client, db, seed_ids, merchant_headers):
    resp = client.patch(
        f"/api/v1/merchant/products/{seed_ids['product_id']}",
        json={"price": 5000},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["price"] == 5000
    assert data["product_id"] == seed_ids["product_id"]

    db.expire_all()
    history = (
        db.query(ProductPriceHistory)
        .filter(ProductPriceHistory.product_id == seed_ids["product_id"])
        .first()
    )
    assert history is not None
    assert history.old_price == 3000
    assert history.new_price == 5000
    assert history.reason.value == "manual"


def test_patch_stock_status(client, db, seed_ids, merchant_headers):
    resp = client.patch(
        f"/api/v1/merchant/products/{seed_ids['product_id']}",
        json={"stock_status": "low_stock"},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stock_status"] == "low_stock"

    db.expire_all()
    p = db.query(Product).filter(Product.product_id == seed_ids["product_id"]).first()
    assert p.stock_status == StockStatusEnum.low_stock


def test_patch_other_merchant_product_403(client, seed_ids, other_merchant_headers):
    resp = client.patch(
        f"/api/v1/merchant/products/{seed_ids['product_id']}",
        json={"price": 9999},
        headers=other_merchant_headers,
    )
    assert resp.status_code == 403


def test_get_my_store(client, seed_ids, merchant_headers):
    resp = client.get("/api/v1/merchant/my-store", headers=merchant_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["store_id"] == seed_ids["store_id"]
    assert "store_name" in data
    assert "zone_label" in data
    assert "market_id" in data


def test_get_store_products(client, seed_ids):
    resp = client.get(f"/api/v1/stores/{seed_ids['store_id']}/products")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "items" in data
    assert len(data["items"]) >= 1
    item = data["items"][0]
    assert "product_id" in item
    assert "product_name" in item
    assert "price" in item
    assert "stock_status" in item
