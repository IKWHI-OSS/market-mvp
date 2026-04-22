import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # MUST come before "from app.main import app"
from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum, ShoppingList, ShoppingListItem
from app.core.security import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test_shopping_lists.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_shopping_lists.db"):
        os.remove("test_shopping_lists.db")


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
        email=f"shoplist_{uuid.uuid4().hex[:6]}@test.com",
        password=hash_password("password123"),
        role=RoleEnum.consumer,
        name="쇼핑리스트테스터",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id.in_(
            db.query(ShoppingList.shopping_list_id).filter(ShoppingList.user_id == user.user_id)
        )
    ).delete(synchronize_session=False)
    db.query(ShoppingList).filter(ShoppingList.user_id == user.user_id).delete()
    db.query(User).filter(User.user_id == user.user_id).delete()
    db.commit()


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user.user_id, "role": test_user.role.value})


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Test 1: GET /shopping-lists with valid token → empty list initially ──────

def test_get_shopping_lists_empty(client, auth_headers):
    resp = client.get("/api/v1/shopping-lists", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


# ── Test 2: POST /shopping-lists → creates list, returns with item_count=0 ───

def test_create_shopping_list(client, auth_headers):
    resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "장보기 목록"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["title"] == "장보기 목록"
    assert data["item_count"] == 0
    assert data["total_estimated_price"] is None
    assert "shopping_list_id" in data
    assert "created_at" in data


# ── Test 3: GET /shopping-lists after create → returns 1 list ────────────────

def test_get_shopping_lists_after_create(client, auth_headers):
    # Create one list first
    client.post(
        "/api/v1/shopping-lists",
        json={"title": "두 번째 목록"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/shopping-lists", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    # At least one list present
    assert len(body["data"]) >= 1
    titles = [item["title"] for item in body["data"]]
    assert "두 번째 목록" in titles


# ── Test 4: POST items with all required fields → 200, item returned ─────────

def test_add_item_success(client, auth_headers):
    # Create a list first
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "아이템 테스트 목록"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "사과", "qty": 2, "unit": "개"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["product_name_snapshot"] == "사과"
    assert data["qty"] == 2
    assert data["unit"] == "개"
    assert data["checked"] is False
    assert data["estimated_price"] is None
    assert data["shopping_list_id"] == sl_id
    assert "list_item_id" in data


# ── Test 5: POST items missing unit → 422 ────────────────────────────────────

def test_add_item_missing_unit(client, auth_headers):
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "유효성 테스트"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "배", "qty": 1},  # missing unit
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── Test 6: POST items on non-existent list → 404 ────────────────────────────

def test_add_item_nonexistent_list(client, auth_headers):
    fake_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/shopping-lists/{fake_id}/items",
        json={"product_name_snapshot": "감", "qty": 3, "unit": "개"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── Test 7: PATCH item checked=true → checked field updated ──────────────────

def test_patch_item_checked(client, db, auth_headers, test_user):
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "패치 테스트 목록"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    item_resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "포도", "qty": 1, "unit": "송이"},
        headers=auth_headers,
    )
    item_id = item_resp.json()["data"]["list_item_id"]

    patch_resp = client.patch(
        f"/api/v1/shopping-lists/{sl_id}/items/{item_id}",
        json={"checked": True},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()["data"]
    assert data["checked"] is True

    # Also verify DB state
    db_item = db.query(ShoppingListItem).filter(
        ShoppingListItem.list_item_id == item_id
    ).first()
    assert db_item is not None
    assert db_item.checked is True


# ── Test 8: PATCH item on wrong list_id → 404 ────────────────────────────────

def test_patch_item_wrong_list(client, auth_headers):
    # Create a list and add an item
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "잘못된 리스트 테스트"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    item_resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "딸기", "qty": 1, "unit": "팩"},
        headers=auth_headers,
    )
    item_id = item_resp.json()["data"]["list_item_id"]

    fake_list_id = str(uuid.uuid4())
    resp = client.patch(
        f"/api/v1/shopping-lists/{fake_list_id}/items/{item_id}",
        json={"checked": True},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── Test 9: DELETE item → 200, deleted=true ───────────────────────────────────

def test_delete_item(client, auth_headers):
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "삭제 테스트 목록"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    item_resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "오렌지", "qty": 4, "unit": "개"},
        headers=auth_headers,
    )
    item_id = item_resp.json()["data"]["list_item_id"]

    del_resp = client.delete(
        f"/api/v1/shopping-lists/{sl_id}/items/{item_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 200
    body = del_resp.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


# ── Test 10: DELETE again (already deleted) → 404 ────────────────────────────

def test_delete_item_already_deleted(client, auth_headers):
    create_resp = client.post(
        "/api/v1/shopping-lists",
        json={"title": "중복삭제 테스트 목록"},
        headers=auth_headers,
    )
    sl_id = create_resp.json()["data"]["shopping_list_id"]

    item_resp = client.post(
        f"/api/v1/shopping-lists/{sl_id}/items",
        json={"product_name_snapshot": "레몬", "qty": 2, "unit": "개"},
        headers=auth_headers,
    )
    item_id = item_resp.json()["data"]["list_item_id"]

    # First delete succeeds
    client.delete(
        f"/api/v1/shopping-lists/{sl_id}/items/{item_id}",
        headers=auth_headers,
    )

    # Second delete → 404
    resp = client.delete(
        f"/api/v1/shopping-lists/{sl_id}/items/{item_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 404
