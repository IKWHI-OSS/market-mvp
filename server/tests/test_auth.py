import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # ensures all models are registered with Base.metadata

from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum
from app.core.security import hash_password

_TEST_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
os.makedirs(_TEST_DB_DIR, exist_ok=True)
TEST_DB_URL = f"sqlite:///{os.path.join(_TEST_DB_DIR, 'test_auth.db')}"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    _db_path = os.path.join(_TEST_DB_DIR, "test_auth.db")
    if os.path.exists(_db_path):
        os.remove(_db_path)


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
        email="consumer@test.com",
        password=hash_password("password123"),
        role=RoleEnum.consumer,
        name="테스트소비자",
    )
    db.add(user)
    db.commit()
    yield user
    db.query(User).filter(User.email == "consumer@test.com").delete()
    db.commit()


def test_login_success(client, test_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "consumer@test.com", "password": "password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["role"] == "consumer"
    assert body["data"]["home_screen_id"] == "SCR-C-01"


def test_login_wrong_password(client, test_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "consumer@test.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["success"] is False
    assert resp.json()["code"] == "UNAUTHORIZED"


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "anything"},
    )
    assert resp.status_code == 401


def test_me_with_valid_token(client, test_user):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "consumer@test.com", "password": "password123"},
    )
    token = login.json()["data"]["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "consumer@test.com"


def test_me_without_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["success"] is False


def test_me_invalid_token(client):
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert resp.status_code == 401
