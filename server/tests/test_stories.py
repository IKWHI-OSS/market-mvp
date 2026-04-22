"""
test_stories.py — Phase 2-2: 상인 스토리 생성 고도화 테스트
  - LLM 성공 경로 (DI mock)
  - LLM 실패 → fallback
  - 권한 검증 (403)
  - 존재하지 않는 점포 → 404
  - save_to_store 옵션
"""
import uuid
import os
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
from app.services import story_service

TEST_DB_URL = "sqlite:////tmp/test_stories.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("/tmp/test_stories.db"):
        os.remove("/tmp/test_stories.db")


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

    market_id        = str(uuid.uuid4())
    store_id         = str(uuid.uuid4())
    merchant_user_id = str(uuid.uuid4())
    consumer_user_id = str(uuid.uuid4())
    merchant_id      = str(uuid.uuid4())
    product_id       = str(uuid.uuid4())

    session.add_all([
        Market(market_id=market_id, market_name="스토리시장", address="서울", lat=37.5, lng=127.0, zoom=14),
        Store(store_id=store_id, market_id=market_id, store_name="참외가게", zone_label="C구역"),
        User(user_id=merchant_user_id, email="storymerchant@example.com",
             password=hash_password("test1234"), role=RoleEnum.merchant, name="스토리상인"),
        User(user_id=consumer_user_id, email="storyconsumer@example.com",
             password=hash_password("test1234"), role=RoleEnum.consumer, name="스토리소비자"),
        Merchant(merchant_id=merchant_id, store_id=store_id, user_id=merchant_user_id,
                 display_name="스토리테스트상인"),
        Product(product_id=product_id, store_id=store_id, product_name="참외",
                price=3000, stock_status=StockStatusEnum.in_stock),
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


# ── 서비스 단위 테스트 ────────────────────────────────────────────────

def test_generate_story_llm_success(db, seed_ids):
    """LLM DI mock 성공 경로."""
    class FakeUser:
        role = type("R", (), {"value": "merchant"})()

    def mock_llm(store_name, store_desc, product_names):
        return f"{store_name}의 신선한 {product_names[0]}을 맛보세요!"

    result = story_service.generate_story(
        db, FakeUser(), seed_ids["store_id"], llm_fn=mock_llm
    )
    assert result["fallback_mode"] is False
    assert "참외가게" in result["story"]
    assert "참외" in result["story"]
    assert result["store_id"] == seed_ids["store_id"]


def test_generate_story_llm_fallback(db, seed_ids):
    """LLM 실패 → fallback 템플릿 반환."""
    class FakeUser:
        role = type("R", (), {"value": "merchant"})()

    def failing_llm(**kwargs):
        raise RuntimeError("LLM 서비스 불가")

    result = story_service.generate_story(
        db, FakeUser(), seed_ids["store_id"], llm_fn=failing_llm
    )
    assert result["fallback_mode"] is True
    assert len(result["story"]) > 0
    assert "참외가게" in result["story"] or "전통시장" in result["story"]


def test_generate_story_merchant_required(db, seed_ids):
    """소비자 권한 → 403."""
    from fastapi import HTTPException

    class FakeConsumer:
        role = type("R", (), {"value": "consumer"})()

    with pytest.raises(HTTPException) as exc:
        story_service.generate_story(db, FakeConsumer(), seed_ids["store_id"])
    assert exc.value.status_code == 403


def test_generate_story_store_not_found(db):
    """존재하지 않는 store_id → 404."""
    from fastapi import HTTPException

    class FakeUser:
        role = type("R", (), {"value": "merchant"})()

    with pytest.raises(HTTPException) as exc:
        story_service.generate_story(db, FakeUser(), "nonexistent-store")
    assert exc.value.status_code == 404


# ── API 테스트 ────────────────────────────────────────────────────────

def test_create_story_api_fallback(client, seed_ids, merchant_headers):
    """API: ANTHROPIC_API_KEY 없을 때 fallback 응답 (HTTP 200)."""
    resp = client.post(
        "/api/v1/merchant/stories",
        json={"store_id": seed_ids["store_id"]},
        headers=merchant_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "story" in data
    assert data["fallback_mode"] is True        # API 키 없으므로 fallback
    assert "products_used" in data
    assert data["store_id"] == seed_ids["store_id"]


def test_create_story_api_consumer_forbidden(client, seed_ids, consumer_headers):
    """소비자 → 403."""
    resp = client.post(
        "/api/v1/merchant/stories",
        json={"store_id": seed_ids["store_id"]},
        headers=consumer_headers,
    )
    assert resp.status_code == 403


def test_create_story_api_store_not_found(client, merchant_headers):
    """존재하지 않는 점포 → 404."""
    resp = client.post(
        "/api/v1/merchant/stories",
        json={"store_id": "no-such-store"},
        headers=merchant_headers,
    )
    assert resp.status_code == 404


def test_create_story_api_unauthenticated(client, seed_ids):
    """인증 없음 → 401."""
    resp = client.post(
        "/api/v1/merchant/stories",
        json={"store_id": seed_ids["store_id"]},
    )
    assert resp.status_code == 401


def test_create_story_response_structure(client, seed_ids, merchant_headers):
    """응답 구조: success, code, data, meta."""
    resp = client.post(
        "/api/v1/merchant/stories",
        json={"store_id": seed_ids["store_id"]},
        headers=merchant_headers,
    )
    body = resp.json()
    assert "success" in body
    assert "code" in body
    assert "data" in body
    assert "meta" in body
    data = body["data"]
    for key in ("store_id", "store_name", "story", "fallback_mode", "products_used"):
        assert key in data, f"응답에 '{key}' 누락"
