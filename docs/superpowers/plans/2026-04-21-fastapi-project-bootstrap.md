# FastAPI Project Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `server/` 아래에 FastAPI MVP 백엔드를 구성한다 — DB 연결, SQLAlchemy 모델 11개, 공통 응답/에러 규약, JWT 인증, 홈 피드 API까지.

**Architecture:** SQLAlchemy 2.x + PyMySQL로 Railway MySQL에 연결하고, 계층은 `models → repositories → services → routers` 순서로 분리한다. 공통 응답 포맷은 모든 엔드포인트에서 `BaseResponse`로 통일한다.

**Tech Stack:** Python 3.11+, FastAPI 0.115, SQLAlchemy 2.0, PyMySQL 1.1, python-jose, passlib[bcrypt], pydantic-settings 2.x, pytest + SQLite(테스트용)

---

## 파일 구조 (전체)

```
server/
  requirements.txt
  .env.example
  app/
    __init__.py
    main.py
    core/
      __init__.py
      config.py         # pydantic-settings로 .env 읽기
      security.py       # JWT encode/decode, bcrypt 해시
      exceptions.py     # 공통 에러 핸들러 함수 모음
    db/
      __init__.py
      session.py        # engine, SessionLocal, Base, get_db
      models/
        __init__.py     # 모든 모델 재-export (metadata 등록)
        user.py
        market.py
        store.py
        merchant.py
        product.py
        drop_event.py
        catalog_item.py
        shopping_list.py
        shopping_list_item.py
        route_plan.py
        notification.py
      repositories/
        __init__.py
        user_repository.py
        home_repository.py
    schemas/
      __init__.py
      common.py         # BaseResponse, Meta, success_response()
      auth.py           # LoginRequest, LoginResponse, UserOut
      home.py           # HomeData, DropHeroItem, EventCard, StoreSpotlight
    services/
      __init__.py
      auth_service.py   # login(), get_current_user dependency
      home_service.py   # get_home_feed()
    api/
      __init__.py
      v1/
        __init__.py
        router.py       # 모든 라우터 통합
        auth.py         # POST /auth/login, GET /auth/me
        home.py         # GET /home
  tests/
    __init__.py
    conftest.py         # SQLite 테스트 DB, TestClient fixture
    test_auth.py
    test_home.py
```

---

## Task 1: 프로젝트 스켈레톤

**Files:**
- Create: `server/requirements.txt`
- Create: `server/.env.example`
- Create: `server/app/__init__.py` (빈 파일)
- Create: `server/app/core/__init__.py`
- Create: `server/app/db/__init__.py`
- Create: `server/app/db/models/__init__.py` (우선 빈 파일, Task 3·4에서 채움)
- Create: `server/app/db/repositories/__init__.py`
- Create: `server/app/schemas/__init__.py`
- Create: `server/app/services/__init__.py`
- Create: `server/app/api/__init__.py`
- Create: `server/app/api/v1/__init__.py`
- Create: `server/tests/__init__.py`

- [ ] **Step 1: requirements.txt 작성**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.36
pymysql==1.1.1
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.9.2
pydantic-settings==2.5.2
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

파일 경로: `server/requirements.txt`

- [ ] **Step 2: .env.example 작성**

```
DATABASE_URL=mysql+pymysql://user:password@host:3306/market_mvp
SECRET_KEY=change-this-to-a-random-64-char-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

파일 경로: `server/.env.example`

- [ ] **Step 3: 빈 __init__.py 파일들 생성**

아래 경로에 각각 내용 없는(또는 한 줄 빈) 파일을 생성한다.

```
server/app/__init__.py
server/app/core/__init__.py
server/app/db/__init__.py
server/app/db/models/__init__.py
server/app/db/repositories/__init__.py
server/app/schemas/__init__.py
server/app/services/__init__.py
server/app/api/__init__.py
server/app/api/v1/__init__.py
server/tests/__init__.py
```

- [ ] **Step 4: 패키지 설치 확인**

```bash
cd server
pip install -r requirements.txt
```

Expected: 에러 없이 설치 완료.

- [ ] **Step 5: Commit**

```bash
git add server/requirements.txt server/.env.example server/app server/tests
git commit -m "chore: FastAPI project skeleton and requirements"
```

---

## Task 2: Core Config + DB Session

**Files:**
- Create: `server/app/core/config.py`
- Create: `server/app/db/session.py`

- [ ] **Step 1: config.py 작성**

```python
# server/app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = {"env_file": ".env"}


settings = Settings()
```

- [ ] **Step 2: session.py 작성**

```python
# server/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 3: .env 파일이 있는지 확인 (없으면 .env.example 복사)**

```bash
cd server
ls .env 2>/dev/null || cp .env.example .env
```

- [ ] **Step 4: Python import 검증**

```bash
cd server
python -c "from app.core.config import settings; print(settings.ALGORITHM)"
```

Expected: `HS256`

- [ ] **Step 5: Commit**

```bash
git add server/app/core/config.py server/app/db/session.py
git commit -m "feat: core config and SQLAlchemy session setup"
```

---

## Task 3: SQLAlchemy Models — User · Market · Store · Merchant · Product

**Files:**
- Create: `server/app/db/models/user.py`
- Create: `server/app/db/models/market.py`
- Create: `server/app/db/models/store.py`
- Create: `server/app/db/models/merchant.py`
- Create: `server/app/db/models/product.py`

- [ ] **Step 1: user.py 작성**

```python
# server/app/db/models/user.py
import enum
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class RoleEnum(str, enum.Enum):
    consumer = "consumer"
    merchant = "merchant"
    operator = "operator"


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    home_market_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 2: market.py 작성**

```python
# server/app/db/models/market.py
from sqlalchemy import Column, String, DECIMAL, Text, DateTime
from sqlalchemy.sql import func

from app.db.session import Base


class Market(Base):
    __tablename__ = "market"

    market_id = Column(String(36), primary_key=True)
    market_name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    lat = Column(DECIMAL(10, 7), nullable=False)
    lng = Column(DECIMAL(10, 7), nullable=False)
    region_code = Column(String(20), nullable=True)
    zoom = Column(DECIMAL(5, 2), nullable=False)
    market_desc = Column(Text, nullable=True)
    open_hours = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 3: store.py 작성**

```python
# server/app/db/models/store.py
from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Store(Base):
    __tablename__ = "store"

    store_id = Column(String(36), primary_key=True)
    market_id = Column(String(36), ForeignKey("market.market_id"), nullable=False)
    store_name = Column(String(255), nullable=False)
    zone_label = Column(String(50), nullable=False)
    lat = Column(DECIMAL(10, 7), nullable=True)
    lng = Column(DECIMAL(10, 7), nullable=True)
    phone = Column(String(20), nullable=True)
    status = Column(String(20), nullable=True, default="open")
    store_story_summary = Column(Text, nullable=True)
    open_hours = Column(String(255), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    market = relationship("Market", backref="stores")
    merchants = relationship("Merchant", back_populates="store")
    products = relationship("Product", back_populates="store")
    drop_events = relationship("DropEvent", back_populates="store")
```

- [ ] **Step 4: merchant.py 작성**

```python
# server/app/db/models/merchant.py
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Merchant(Base):
    __tablename__ = "merchant"

    merchant_id = Column(String(36), primary_key=True)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("user.user_id"), nullable=False)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="merchants")
    user = relationship("User", backref="merchant_profile")
```

- [ ] **Step 5: product.py 작성**

```python
# server/app/db/models/product.py
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class StockStatusEnum(str, enum.Enum):
    in_stock = "in_stock"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"


class Product(Base):
    __tablename__ = "product"

    product_id = Column(String(36), primary_key=True)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    price = Column(Integer, nullable=False)
    stock_status = Column(
        Enum(StockStatusEnum), nullable=False, default=StockStatusEnum.in_stock
    )
    image_url = Column(String(500), nullable=True)
    quality_note = Column(Text, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="products")
    drop_events = relationship("DropEvent", back_populates="product")
```

- [ ] **Step 6: Commit**

```bash
git add server/app/db/models/user.py server/app/db/models/market.py \
        server/app/db/models/store.py server/app/db/models/merchant.py \
        server/app/db/models/product.py
git commit -m "feat: SQLAlchemy models - User, Market, Store, Merchant, Product"
```

---

## Task 4: SQLAlchemy Models — DropEvent · CatalogItem · ShoppingList · ShoppingListItem · RoutePlan · Notification

**Files:**
- Create: `server/app/db/models/drop_event.py`
- Create: `server/app/db/models/catalog_item.py`
- Create: `server/app/db/models/shopping_list.py`
- Create: `server/app/db/models/shopping_list_item.py`
- Create: `server/app/db/models/route_plan.py`
- Create: `server/app/db/models/notification.py`
- Modify: `server/app/db/models/__init__.py`

- [ ] **Step 1: drop_event.py 작성**

```python
# server/app/db/models/drop_event.py
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class DropStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    arrived = "arrived"
    sold_out = "sold_out"


class DropEvent(Base):
    __tablename__ = "drop_event"

    drop_id = Column(String(36), primary_key=True)
    product_id = Column(String(36), ForeignKey("product.product_id"), nullable=False)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=False)
    title = Column(String(255), nullable=True)
    expected_at = Column(DateTime, nullable=False)
    status = Column(Enum(DropStatusEnum), nullable=False, default=DropStatusEnum.scheduled)
    subscriber_count = Column(Integer, default=0)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="drop_events")
    store = relationship("Store", back_populates="drop_events")
```

- [ ] **Step 2: catalog_item.py 작성**

```python
# server/app/db/models/catalog_item.py
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class CatalogItemTypeEnum(str, enum.Enum):
    drop = "drop"
    event = "event"
    store_spotlight = "store_spotlight"


class CatalogItem(Base):
    __tablename__ = "catalog_item"

    catalog_item_id = Column(String(36), primary_key=True)
    market_id = Column(String(36), ForeignKey("market.market_id"), nullable=False)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=True)
    product_id = Column(String(36), ForeignKey("product.product_id"), nullable=True)
    item_type = Column(Enum(CatalogItemTypeEnum), nullable=False)
    title = Column(String(255), nullable=False)
    title_snapshot = Column(String(255), nullable=False)
    image_snapshot = Column(String(500), nullable=False)
    price_snapshot = Column(Integer, nullable=True)
    badge = Column(String(100), nullable=True)
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    market = relationship("Market", backref="catalog_items")
    store = relationship("Store", backref="catalog_items")
```

- [ ] **Step 3: shopping_list.py 작성**

```python
# server/app/db/models/shopping_list.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShoppingList(Base):
    __tablename__ = "shopping_list"

    shopping_list_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.user_id"), nullable=False)
    title = Column(String(255), nullable=False)
    total_estimated_price = Column(Integer, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list")
```

- [ ] **Step 4: shopping_list_item.py 작성**

```python
# server/app/db/models/shopping_list_item.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_item"

    list_item_id = Column(String(36), primary_key=True)
    shopping_list_id = Column(
        String(36), ForeignKey("shopping_list.shopping_list_id"), nullable=False
    )
    product_id = Column(String(36), ForeignKey("product.product_id"), nullable=True)
    product_name_snapshot = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False)
    unit = Column(String(20), nullable=False)
    checked = Column(Boolean, default=False, nullable=False)
    estimated_price = Column(Integer, nullable=True)
    store_id = Column(String(36), ForeignKey("store.store_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    shopping_list = relationship("ShoppingList", back_populates="items")
```

- [ ] **Step 5: route_plan.py 작성**

```python
# server/app/db/models/route_plan.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class RoutePlan(Base):
    __tablename__ = "route_plan"

    route_plan_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.user_id"), nullable=False)
    market_id = Column(String(36), ForeignKey("market.market_id"), nullable=False)
    shopping_list_id = Column(
        String(36), ForeignKey("shopping_list.shopping_list_id"), nullable=False
    )
    route_json = Column(JSON, nullable=False)
    estimated_minutes = Column(Integer, nullable=True)
    distance_meters = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="route_plans")
    market = relationship("Market", backref="route_plans")
```

- [ ] **Step 6: notification.py 작성**

```python
# server/app/db/models/notification.py
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Notification(Base):
    __tablename__ = "notification"

    notification_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.user_id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    target_screen_id = Column(String(50), nullable=True)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    send_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="notifications")
```

- [ ] **Step 7: models/__init__.py 업데이트 — 모든 모델 등록**

```python
# server/app/db/models/__init__.py
from app.db.models.user import User, RoleEnum
from app.db.models.market import Market
from app.db.models.store import Store
from app.db.models.merchant import Merchant
from app.db.models.product import Product, StockStatusEnum
from app.db.models.drop_event import DropEvent, DropStatusEnum
from app.db.models.catalog_item import CatalogItem, CatalogItemTypeEnum
from app.db.models.shopping_list import ShoppingList
from app.db.models.shopping_list_item import ShoppingListItem
from app.db.models.route_plan import RoutePlan
from app.db.models.notification import Notification

__all__ = [
    "User", "RoleEnum",
    "Market",
    "Store",
    "Merchant",
    "Product", "StockStatusEnum",
    "DropEvent", "DropStatusEnum",
    "CatalogItem", "CatalogItemTypeEnum",
    "ShoppingList",
    "ShoppingListItem",
    "RoutePlan",
    "Notification",
]
```

- [ ] **Step 8: import 검증**

```bash
cd server
python -c "from app.db.models import User, DropEvent, CatalogItem; print('OK')"
```

Expected: `OK`

- [ ] **Step 9: Commit**

```bash
git add server/app/db/models/
git commit -m "feat: SQLAlchemy models - DropEvent, CatalogItem, ShoppingList, RoutePlan, Notification"
```

---

## Task 5: 공통 응답 스키마 + 에러 핸들러 + main.py 초안

**Files:**
- Create: `server/app/schemas/common.py`
- Create: `server/app/core/exceptions.py`
- Create: `server/app/main.py`

- [ ] **Step 1: 실패 테스트 작성 (에러 핸들러 존재 여부)**

파일: `server/tests/test_common.py`

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_404_returns_standard_error():
    resp = client.get("/api/v1/nonexistent-endpoint")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == "NOT_FOUND"


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_common.py -v
```

Expected: FAIL (app.main 모듈 없음)

- [ ] **Step 3: common.py 작성**

```python
# server/app/schemas/common.py
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel


class Meta(BaseModel):
    request_id: str
    timestamp: str


class BaseResponse(BaseModel):
    success: bool = True
    code: str = "OK"
    message: str = "요청이 성공했습니다."
    data: Any = None
    meta: Optional[Meta] = None


def success_response(data: Any, message: str = "요청이 성공했습니다.") -> BaseResponse:
    return BaseResponse(
        data=data,
        message=message,
        meta=Meta(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )
```

- [ ] **Step 4: exceptions.py 작성**

```python
# server/app/core/exceptions.py
import uuid
from datetime import datetime, timezone

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

_HTTP_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    500: "INTERNAL_ERROR",
    503: "AI_UNAVAILABLE",
}


def _make_error_body(code: str, message: str) -> dict:
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": None,
        "meta": {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = _HTTP_CODE_MAP.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=_make_error_body(code, str(exc.detail)),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first_msg = exc.errors()[0].get("msg", "Validation error") if exc.errors() else "Validation error"
    return JSONResponse(
        status_code=422,
        content=_make_error_body("VALIDATION_ERROR", str(first_msg)),
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_make_error_body("INTERNAL_ERROR", "서버 오류가 발생했습니다."),
    )
```

- [ ] **Step 5: main.py 작성**

```python
# server/app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="Market Info API", version="1.0.0")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/health")
def health():
    return {"status": "ok"}
```

라우터 연결은 Task 7 완료 후 추가한다.

- [ ] **Step 6: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_common.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 7: Commit**

```bash
git add server/app/schemas/common.py server/app/core/exceptions.py \
        server/app/main.py server/tests/test_common.py
git commit -m "feat: common response schema, error handlers, and FastAPI app bootstrap"
```

---

## Task 6: Security 모듈 (JWT + bcrypt)

**Files:**
- Create: `server/app/core/security.py`
- Test: `server/tests/test_security.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# server/tests/test_security.py
from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_and_verify():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    payload = {"user_id": "user_001", "role": "consumer"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == "user_001"
    assert decoded["role"] == "consumer"


def test_expired_token_raises():
    from datetime import timedelta
    from jose import JWTError
    import pytest
    token = create_access_token({"user_id": "x"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        decode_token(token)
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_security.py -v
```

Expected: FAIL (security 모듈 없음)

- [ ] **Step 3: security.py 작성**

```python
# server/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_security.py -v
```

Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add server/app/core/security.py server/tests/test_security.py
git commit -m "feat: JWT and bcrypt security module"
```

---

## Task 7: Auth 도메인 (schemas + repository + service + router)

**Files:**
- Create: `server/app/schemas/auth.py`
- Create: `server/app/db/repositories/user_repository.py`
- Create: `server/app/services/auth_service.py`
- Create: `server/app/api/v1/auth.py`
- Create: `server/app/api/v1/router.py`
- Modify: `server/app/main.py` (router 연결)
- Test: `server/tests/test_auth.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# server/tests/test_auth.py
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, RoleEnum
from app.core.security import hash_password

import app.db.models  # 모델 등록 보장

TEST_DB_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


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
    return user


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
    assert resp.status_code == 403
    assert resp.json()["success"] is False


def test_me_invalid_token(client):
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert resp.status_code == 401
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_auth.py -v
```

Expected: FAIL (auth 모듈 없음)

- [ ] **Step 3: auth.py 스키마 작성**

```python
# server/app/schemas/auth.py
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    user_id: str
    email: str
    role: str
    name: str
```

- [ ] **Step 4: user_repository.py 작성**

```python
# server/app/db/repositories/user_repository.py
from sqlalchemy.orm import Session

from app.db.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()
```

- [ ] **Step 5: auth_service.py 작성**

```python
# server/app/services/auth_service.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token, verify_password
from app.db.models.user import User
from app.db.repositories.user_repository import get_user_by_email, get_user_by_id
from app.db.session import get_db

_bearer = HTTPBearer()

_HOME_SCREEN = {
    "consumer": "SCR-C-01",
    "merchant": "SCR-M-01",
    "operator": "SCR-C-01",
}


def login(email: str, password: str, db: Session) -> dict:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    token = create_access_token({"user_id": user.user_id, "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
        },
        "home_screen_id": _HOME_SCREEN.get(user.role.value, "SCR-C-01"),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload["user_id"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user
```

- [ ] **Step 6: api/v1/auth.py 작성**

```python
# server/app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest
from app.schemas.common import BaseResponse, success_response
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=BaseResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    data = auth_service.login(req.email, req.password, db)
    return success_response(data)


@router.get("/me", response_model=BaseResponse)
def me(current_user: User = Depends(auth_service.get_current_user)):
    return success_response({
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role.value,
        "name": current_user.name,
    })
```

- [ ] **Step 7: api/v1/router.py 작성**

```python
# server/app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import auth

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
```

홈 라우터는 Task 8 완료 후 추가한다.

- [ ] **Step 8: main.py에 라우터 연결**

`server/app/main.py` 하단에 아래 두 줄 추가:

```python
# 기존 import 블록 맨 위에 추가
from app.api.v1.router import router as api_router

# app 선언 직후 (exception_handler 등록 아래)에 추가
app.include_router(api_router)
```

전체 `main.py`:

```python
# server/app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import router as api_router
from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="Market Info API", version="1.0.0")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 9: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_auth.py -v
```

Expected: PASS (7 tests)

- [ ] **Step 10: Commit**

```bash
git add server/app/schemas/auth.py \
        server/app/db/repositories/user_repository.py \
        server/app/services/auth_service.py \
        server/app/api/v1/auth.py \
        server/app/api/v1/router.py \
        server/app/main.py \
        server/tests/test_auth.py
git commit -m "feat: auth domain - login JWT, /auth/login, /auth/me"
```

---

## Task 8: Home 도메인 (schemas + repository + service + router)

**Files:**
- Create: `server/app/schemas/home.py`
- Create: `server/app/db/repositories/home_repository.py`
- Create: `server/app/services/home_service.py`
- Create: `server/app/api/v1/home.py`
- Modify: `server/app/api/v1/router.py`
- Test: `server/tests/test_home.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# server/tests/test_home.py
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
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

import app.db.models  # 모델 등록 보장

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
def seeded_db():
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
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_home.py -v
```

Expected: FAIL (home 모듈 없음)

- [ ] **Step 3: home.py 스키마 작성**

```python
# server/app/schemas/home.py
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DropHeroItem(BaseModel):
    drop_id: str
    product_id: str
    store_id: str
    title: Optional[str]
    image_url: Optional[str]
    status: str
    expected_at: str


class EventCard(BaseModel):
    catalog_item_id: str
    title: str
    image_url: str


class StoreSpotlight(BaseModel):
    store_id: str
    store_name: str
    summary: str
    image_url: str


class HomeData(BaseModel):
    market: Optional[Dict[str, Any]]
    drop_hero: List[DropHeroItem]
    event_cards: List[EventCard]
    store_spotlights: List[StoreSpotlight]
```

- [ ] **Step 4: home_repository.py 작성**

```python
# server/app/db/repositories/home_repository.py
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.catalog_item import CatalogItem, CatalogItemTypeEnum
from app.db.models.drop_event import DropEvent, DropStatusEnum
from app.db.models.market import Market
from app.db.models.product import Product
from app.db.models.store import Store


def get_drop_hero(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = (
        db.query(DropEvent, Product.image_url)
        .join(Product, DropEvent.product_id == Product.product_id)
        .filter(DropEvent.status.in_([DropStatusEnum.scheduled, DropStatusEnum.arrived]))
    )
    if market_id:
        query = query.join(Store, DropEvent.store_id == Store.store_id).filter(
            Store.market_id == market_id
        )
    return query.order_by(DropEvent.expected_at).limit(limit).all()


def get_event_cards(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = db.query(CatalogItem).filter(
        CatalogItem.item_type == CatalogItemTypeEnum.event
    )
    if market_id:
        query = query.filter(CatalogItem.market_id == market_id)
    return query.order_by(CatalogItem.priority.desc()).limit(limit).all()


def get_store_spotlights(db: Session, market_id: Optional[str] = None, limit: int = 5):
    query = (
        db.query(CatalogItem, Store.store_name)
        .join(Store, CatalogItem.store_id == Store.store_id)
        .filter(CatalogItem.item_type == CatalogItemTypeEnum.store_spotlight)
    )
    if market_id:
        query = query.filter(CatalogItem.market_id == market_id)
    return query.order_by(CatalogItem.priority.desc()).limit(limit).all()


def get_market(db: Session, market_id: str) -> Optional[Market]:
    return db.query(Market).filter(Market.market_id == market_id).first()
```

- [ ] **Step 5: home_service.py 작성**

```python
# server/app/services/home_service.py
from typing import Optional

from sqlalchemy.orm import Session

from app.db.repositories.home_repository import (
    get_drop_hero,
    get_event_cards,
    get_market,
    get_store_spotlights,
)


def get_home_feed(db: Session, market_id: Optional[str] = None) -> dict:
    drops = get_drop_hero(db, market_id)
    events = get_event_cards(db, market_id)
    spotlights = get_store_spotlights(db, market_id)
    market = get_market(db, market_id) if market_id else None

    drop_hero = [
        {
            "drop_id": drop.drop_id,
            "product_id": drop.product_id,
            "store_id": drop.store_id,
            "title": drop.title,
            "image_url": image_url,
            "status": drop.status.value,
            "expected_at": drop.expected_at.isoformat(),
        }
        for drop, image_url in drops
    ]

    event_cards = [
        {
            "catalog_item_id": c.catalog_item_id,
            "title": c.title,
            "image_url": c.image_snapshot,
        }
        for c in events
    ]

    store_spotlights = [
        {
            "store_id": c.store_id,
            "store_name": store_name,
            "summary": c.title_snapshot,
            "image_url": c.image_snapshot,
        }
        for c, store_name in spotlights
    ]

    return {
        "market": (
            {"market_id": market.market_id, "market_name": market.market_name}
            if market
            else None
        ),
        "drop_hero": drop_hero,
        "event_cards": event_cards,
        "store_spotlights": store_spotlights,
    }
```

- [ ] **Step 6: api/v1/home.py 작성**

```python
# server/app/api/v1/home.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import home_service

router = APIRouter(tags=["home"])


@router.get("/home", response_model=BaseResponse)
def get_home(
    market_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = home_service.get_home_feed(db, market_id)
    return success_response(data)
```

- [ ] **Step 7: router.py에 홈 라우터 추가**

```python
# server/app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import auth, home

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(home.router)
```

- [ ] **Step 8: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_home.py -v
```

Expected: PASS (6 tests)

- [ ] **Step 9: 전체 테스트 실행**

```bash
cd server
python -m pytest tests/ -v
```

Expected: 모든 테스트 PASS (test_common 2개 + test_security 3개 + test_auth 7개 + test_home 6개 = 18개)

- [ ] **Step 10: 서버 기동 확인**

```bash
cd server
uvicorn app.main:app --reload --port 8000
```

별도 터미널에서:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:8000/api/v1/home
# Expected: {"success":true,"code":"OK","data":{"market":null,"drop_hero":[],...}}
```

- [ ] **Step 11: Commit**

```bash
git add server/app/schemas/home.py \
        server/app/db/repositories/home_repository.py \
        server/app/services/home_service.py \
        server/app/api/v1/home.py \
        server/app/api/v1/router.py \
        server/tests/test_home.py
git commit -m "feat: home feed API - drop_hero, event_cards, store_spotlights"
```

---

## Self-Review: Spec vs Plan 커버리지 점검

| 요구사항 | 담당 Task | 상태 |
|---|---|---|
| requirements.txt | Task 1 | ✅ |
| .env.example (DATABASE_URL, SECRET_KEY, ALGORITHM, EXPIRE) | Task 1 | ✅ |
| DB 연결: MySQL + SQLAlchemy + PyMySQL + .env | Task 2 | ✅ |
| SQLAlchemy 모델 11개 (ERD 기준) | Task 3·4 | ✅ |
| 공통 응답 포맷 (success/code/message/data/meta) | Task 5 | ✅ |
| 에러 핸들러 400/401/403/404/409/422/500/503 | Task 5 | ✅ |
| POST /api/v1/auth/login (email+password → JWT, role) | Task 7 | ✅ |
| GET /api/v1/auth/me (JWT → user 정보) | Task 7 | ✅ |
| GET /api/v1/home (drop_hero/event_cards/store_spotlights) | Task 8 | ✅ |

> **미포함 (MVP 이후):** Preorder 모델, operator 역할 API, 결제/정산, 소셜 로그인
