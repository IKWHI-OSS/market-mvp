import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa
from app.core.security import create_access_token, hash_password
from app.db.models import Market, Product, RoleEnum, ShoppingList, ShoppingListItem, Store, User
from app.db.models.product import StockStatusEnum
from app.db.session import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_shopping_agent.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_shopping_agent.db"):
        os.remove("test_shopping_agent.db")


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
        address="서울",
        lat=37.5,
        lng=127.0,
        zoom=14,
    )
    user = User(
        user_id=str(uuid.uuid4()),
        email=f"agent_{uuid.uuid4().hex[:6]}@test.com",
        password=hash_password("password123"),
        role=RoleEnum.consumer,
        name="에이전트테스터",
    )
    store_a = Store(
        store_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_name="우리축산",
        zone_label="B구역",
    )
    store_b = Store(
        store_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_name="진흥청과",
        zone_label="A구역",
    )
    products = [
        Product(
            product_id=str(uuid.uuid4()),
            store_id=store_a.store_id,
            product_name="국내산 돼지고기",
            category="축산",
            price=7800,
            stock_status=StockStatusEnum.in_stock,
        ),
        Product(
            product_id=str(uuid.uuid4()),
            store_id=store_b.store_id,
            product_name="제철 햇감자",
            category="채소",
            price=2400,
            stock_status=StockStatusEnum.in_stock,
        ),
        Product(
            product_id=str(uuid.uuid4()),
            store_id=store_b.store_id,
            product_name="애호박",
            category="채소",
            price=3500,
            stock_status=StockStatusEnum.low_stock,
        ),
    ]

    db.add_all([market, user, store_a, store_b] + products)
    db.commit()
    yield {
        "market_id": market.market_id,
        "user_id": user.user_id,
    }

    db.query(ShoppingListItem).delete()
    db.query(ShoppingList).delete()
    db.query(Product).delete()
    db.query(Store).delete()
    db.query(User).delete()
    db.query(Market).delete()
    db.commit()


@pytest.fixture
def auth_headers(seed):
    token = create_access_token({"user_id": seed["user_id"], "role": "consumer"})
    return {"Authorization": f"Bearer {token}"}


def test_agent_success_flow(client, db, seed, auth_headers):
    resp = client.post(
        "/api/v1/shopping-agent/recommendations",
        json={
            "query": "2인 저녁 찌개 재료 추천해줘",
            "people": 2,
            "budget": 20000,
            "market_id": seed["market_id"],
            "save_as_list": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["clarification_needed"] is False
    assert data["stage"] == "menu_list_matching"
    assert data["menu"]["title"]
    assert len(data["ingredients"]) > 0
    assert "rag_source" in data["menu"]
    assert data["shopping_list_id"] is not None

    # 실제 리스트 생성 확인
    sl = (
        db.query(ShoppingList)
        .filter(ShoppingList.shopping_list_id == data["shopping_list_id"])
        .first()
    )
    assert sl is not None


def test_agent_ambiguous_query(client, auth_headers):
    resp = client.post(
        "/api/v1/shopping-agent/recommendations",
        json={"query": "추천해줘"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["clarification_needed"] is True
    assert data["stage"] == "clarification"
    assert data["shopping_list_id"] is None
    assert data["clarification_question"]


def test_agent_matching_failed_returns_general_list(client, auth_headers):
    # 시드되지 않은 market_id를 지정해 매칭을 의도적으로 실패시킨다.
    resp = client.post(
        "/api/v1/shopping-agent/recommendations",
        json={
            "query": "2인 저녁 찌개 재료 추천해줘",
            "market_id": str(uuid.uuid4()),
            "save_as_list": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["clarification_needed"] is False
    assert data["matching_failed"] is True
    assert data["general_list_only"] is True
    assert data["retry_guide"] is not None
