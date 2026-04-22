import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401 — registers all models before app import

from app.main import app
from app.db.session import Base, get_db
from app.db.models import Market, Store, Product, CatalogItem, StockStatusEnum
from app.db.models.catalog_item import CatalogItemTypeEnum

TEST_DB_URL = "sqlite:///./test_catalog.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_catalog.db"):
        os.remove("test_catalog.db")


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
def seed(db):
    market = Market(
        market_id=str(uuid.uuid4()),
        market_name="테스트시장",
        address="서울시 마포구",
        lat=37.5,
        lng=126.9,
        zoom=15,
    )
    db.add(market)
    db.flush()

    store = Store(
        store_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_name="테스트 채소점",
        zone_label="A구역",
        store_story_summary="국내산 친환경 채소 전문점",
    )
    db.add(store)
    db.flush()

    product = Product(
        product_id=str(uuid.uuid4()),
        store_id=store.store_id,
        product_name="유기농 시금치",
        price=3000,
        stock_status=StockStatusEnum.in_stock,
    )
    db.add(product)
    db.flush()

    event_item = CatalogItem(
        catalog_item_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_id=store.store_id,
        item_type=CatalogItemTypeEnum.event,
        title="봄맞이 특가 행사",
        title_snapshot="봄맞이 전통시장 특가 행사",
        image_snapshot="https://example.com/event.jpg",
    )
    db.add(event_item)

    drop_item = CatalogItem(
        catalog_item_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_id=store.store_id,
        item_type=CatalogItemTypeEnum.drop,
        title="단감 드랍",
        title_snapshot="단감 드랍 스냅샷",
        image_snapshot="https://example.com/drop.jpg",
    )
    db.add(drop_item)

    spotlight_item = CatalogItem(
        catalog_item_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_id=store.store_id,
        item_type=CatalogItemTypeEnum.store_spotlight,
        title="추천 점포",
        title_snapshot="오늘의 추천 점포",
        image_snapshot="https://example.com/store.jpg",
    )
    db.add(spotlight_item)

    db.commit()
    return {
        "market": market,
        "store": store,
        "product": product,
        "event_item": event_item,
        "drop_item": drop_item,
    }


def test_get_event_detail(client, seed):
    res = client.get(f"/api/v1/events/{seed['event_item'].catalog_item_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["catalog_item_id"] == seed["event_item"].catalog_item_id
    assert data["title"] == "봄맞이 특가 행사"
    assert data["store_name"] == "테스트 채소점"
    assert data["zone_label"] == "A구역"
    assert data["image_url"] == "https://example.com/event.jpg"


def test_get_event_wrong_type_returns_404(client, seed):
    res = client.get(f"/api/v1/events/{seed['drop_item'].catalog_item_id}")
    assert res.status_code == 404
    assert res.json()["success"] is False


def test_get_event_unknown_id_returns_404(client, seed):
    res = client.get("/api/v1/events/does-not-exist")
    assert res.status_code == 404


def test_get_store_spotlight(client, seed):
    res = client.get(f"/api/v1/stores/{seed['store'].store_id}/spotlight")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["store_id"] == seed["store"].store_id
    assert data["store_name"] == "테스트 채소점"
    assert data["zone_label"] == "A구역"
    assert data["image_url"] == "https://example.com/store.jpg"
    assert len(data["products"]) == 1
    assert data["products"][0]["product_name"] == "유기농 시금치"
    assert data["products"][0]["stock_status"] == "in_stock"


def test_get_store_spotlight_unknown_id_returns_404(client, seed):
    res = client.get("/api/v1/stores/does-not-exist/spotlight")
    assert res.status_code == 404
