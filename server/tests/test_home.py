from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # ensures all models registered with Base.metadata

from app.main import app as fastapi_app
from app.db.session import Base, get_db
from app.db.models import (
    CatalogItem,
    CatalogItemTypeEnum,
    DropEvent,
    DropStatusEnum,
    Market,
    Product,
    StockStatusEnum,
    Store,
)

TEST_DB_URL = "sqlite:///./test_home.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_home.db"):
        os.remove("test_home.db")


@pytest.fixture(scope="module")
def seeded_db(setup_db):
    session = TestingSessionLocal()
    market = Market(
        market_id="market_h001",
        market_name="테스트시장",
        address="서울시 마포구",
        lat=37.5556,
        lng=126.9104,
        zoom=15,
    )
    session.add(market)
    store = Store(
        store_id="store_h001",
        market_id="market_h001",
        store_name="테스트 과일점",
        zone_label="A구역",
    )
    session.add(store)
    product = Product(
        product_id="product_h001",
        store_id="store_h001",
        product_name="테스트 사과",
        price=5000,
        stock_status=StockStatusEnum.in_stock,
        image_url="https://example.com/apple.jpg",
    )
    session.add(product)
    drop = DropEvent(
        drop_id="drop_h001",
        product_id="product_h001",
        store_id="store_h001",
        title="신선 사과 입고",
        expected_at=datetime(2026, 4, 21, 8, 0, 0, tzinfo=timezone.utc),
        status=DropStatusEnum.scheduled,
    )
    session.add(drop)
    event_card = CatalogItem(
        catalog_item_id="catalog_h_ev001",
        market_id="market_h001",
        item_type=CatalogItemTypeEnum.event,
        title="봄맞이 이벤트",
        title_snapshot="봄맞이 이벤트",
        image_snapshot="https://example.com/event.jpg",
        priority=1,
    )
    session.add(event_card)
    spotlight = CatalogItem(
        catalog_item_id="catalog_h_sp001",
        market_id="market_h001",
        store_id="store_h001",
        item_type=CatalogItemTypeEnum.store_spotlight,
        title="오늘의 추천 점포",
        title_snapshot="오늘의 추천 점포",
        image_snapshot="https://example.com/spotlight.jpg",
        priority=1,
    )
    session.add(spotlight)
    session.commit()
    yield session
    session.close()


@pytest.fixture
def client(seeded_db):
    def override():
        yield seeded_db
    fastapi_app.dependency_overrides[get_db] = override
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


def test_home_feed_returns_all_sections(client):
    resp = client.get("/api/v1/home")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "drop_hero" in data
    assert "event_cards" in data
    assert "store_spotlights" in data


def test_home_drop_hero_content(client):
    resp = client.get("/api/v1/home")
    drops = resp.json()["data"]["drop_hero"]
    assert len(drops) >= 1
    drop = drops[0]
    assert drop["drop_id"] == "drop_h001"
    assert drop["status"] == "scheduled"
    assert drop["image_url"] == "https://example.com/apple.jpg"


def test_home_event_cards_content(client):
    events = client.get("/api/v1/home").json()["data"]["event_cards"]
    assert len(events) >= 1
    assert events[0]["catalog_item_id"] == "catalog_h_ev001"


def test_home_store_spotlights_content(client):
    spotlights = client.get("/api/v1/home").json()["data"]["store_spotlights"]
    assert len(spotlights) >= 1
    assert spotlights[0]["store_id"] == "store_h001"
    assert spotlights[0]["store_name"] == "테스트 과일점"


def test_home_with_market_id_returns_market_info(client):
    resp = client.get("/api/v1/home", params={"market_id": "market_h001"})
    assert resp.status_code == 200
    market = resp.json()["data"]["market"]
    assert market is not None
    assert market["market_id"] == "market_h001"


def test_home_with_unknown_market_id_returns_no_market(client):
    resp = client.get("/api/v1/home", params={"market_id": "nonexistent"})
    assert resp.status_code == 200
    assert resp.json()["data"]["market"] is None
