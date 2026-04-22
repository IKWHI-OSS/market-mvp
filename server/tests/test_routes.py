import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # MUST come before "from app.main import app"
from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, ShoppingList, ShoppingListItem, Store, Market, RoutePlan
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test_routes.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_routes.db"):
        os.remove("test_routes.db")


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
        email=f"routes_{uuid.uuid4().hex[:6]}@test.com",
        password=hash_password("password123"),
        role=RoleEnum.consumer,
        name="루트테스터",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).filter(User.user_id == user.user_id).delete()
    db.commit()


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user.user_id, "role": "consumer"})


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def market(db):
    m = Market(
        market_id=str(uuid.uuid4()),
        market_name="망원시장",
        address="서울시 마포구 망원동",
        lat=37.5563,
        lng=126.9057,
        zoom=15.00,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    yield m
    db.query(Market).filter(Market.market_id == m.market_id).delete()
    db.commit()


@pytest.fixture
def store(db, market):
    s = Store(
        store_id=str(uuid.uuid4()),
        market_id=market.market_id,
        store_name="망원 과일나라",
        zone_label="A구역",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    yield s
    db.query(Store).filter(Store.store_id == s.store_id).delete()
    db.commit()


@pytest.fixture
def shopping_list_with_items(db, test_user, store):
    sl = ShoppingList(
        shopping_list_id=str(uuid.uuid4()),
        user_id=test_user.user_id,
        title="테스트 장보기 목록",
    )
    db.add(sl)
    db.commit()
    db.refresh(sl)

    # Item with store_id
    item1 = ShoppingListItem(
        list_item_id=str(uuid.uuid4()),
        shopping_list_id=sl.shopping_list_id,
        product_name_snapshot="사과",
        qty=2,
        unit="개",
        store_id=store.store_id,
    )
    # Item without store_id
    item2 = ShoppingListItem(
        list_item_id=str(uuid.uuid4()),
        shopping_list_id=sl.shopping_list_id,
        product_name_snapshot="두부",
        qty=1,
        unit="모",
        store_id=None,
    )
    db.add(item1)
    db.add(item2)
    db.commit()
    yield sl
    db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == sl.shopping_list_id
    ).delete()
    db.query(ShoppingList).filter(ShoppingList.shopping_list_id == sl.shopping_list_id).delete()
    db.commit()


# ── Test 1: POST /routes/plans → 200, route_json has "steps", navigation_guide present ──

def test_create_route_plan_success(client, auth_headers, market, shopping_list_with_items):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "route_json" in data
    assert "steps" in data["route_json"]
    assert "navigation_guide" in data
    assert "route_plan_id" in data
    assert "created_at" in data


# ── Test 2: Each step has zone_label key (even if null) ──────────────────────────────

def test_each_step_has_zone_label_key(client, auth_headers, market, shopping_list_with_items):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    steps = resp.json()["data"]["route_json"]["steps"]
    assert len(steps) > 0
    for step in steps:
        assert "zone_label" in step


# ── Test 3: Items with store_id → steps contain store info ───────────────────────────

def test_store_items_appear_in_steps(client, auth_headers, market, shopping_list_with_items, store):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    steps = resp.json()["data"]["route_json"]["steps"]
    store_steps = [s for s in steps if s["store_id"] is not None]
    assert len(store_steps) >= 1
    store_step = store_steps[0]
    assert store_step["store_id"] == store.store_id
    assert store_step["store_name"] == "망원 과일나라"
    assert store_step["zone_label"] == "A구역"
    assert "사과" in store_step["items"]


# ── Test 4: Items without store_id → step with store_id=null exists ──────────────────

def test_no_store_items_grouped_in_null_step(client, auth_headers, market, shopping_list_with_items):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    steps = resp.json()["data"]["route_json"]["steps"]
    null_steps = [s for s in steps if s["store_id"] is None]
    assert len(null_steps) == 1
    assert "두부" in null_steps[0]["items"]


# ── Test 5: Invalid shopping_list_id → 404 ───────────────────────────────────────────

def test_create_route_plan_invalid_shopping_list(client, auth_headers, market):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── Test 6: Invalid market_id → 404 ──────────────────────────────────────────────────

def test_create_route_plan_invalid_market(client, auth_headers, shopping_list_with_items):
    resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": str(uuid.uuid4()), "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── Test 7: GET /routes/plans/{id} → 200, navigation_guide correct ───────────────────

def test_get_route_plan_success(client, auth_headers, market, shopping_list_with_items):
    # First create a plan
    create_resp = client.post(
        "/api/v1/routes/plans",
        json={"market_id": market.market_id, "shopping_list_id": shopping_list_with_items.shopping_list_id},
        headers=auth_headers,
    )
    assert create_resp.status_code == 200
    route_plan_id = create_resp.json()["data"]["route_plan_id"]

    # Then retrieve it
    resp = client.get(f"/api/v1/routes/plans/{route_plan_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["route_plan_id"] == route_plan_id
    guide = data["navigation_guide"]
    assert "A구역" in guide
    assert "순서로 이동하세요" in guide


# ── Test 8: GET /routes/plans/unknown → 404 ──────────────────────────────────────────

def test_get_route_plan_not_found(client, auth_headers):
    resp = client.get(f"/api/v1/routes/plans/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404
