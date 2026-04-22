# Mock Data

MVP 개발/시연용 목 데이터. Railway MySQL DB 초기 세팅 시 아래 순서대로 실행한다.

## 실행 순서

### 1. 스키마 적용 (최초 1회)

```bash
mysql -u root -p -h roundhouse.proxy.rlwy.net -P 55580 market_mvp < db/schema.sql
```

### 2. 테이블 확인 (선택)

```bash
cd server
python -m scripts.init_db
```

SQLAlchemy 모델 기준으로 누락된 테이블만 생성한다 (`checkfirst=True`). 이미 스키마가 적용된 경우 아무것도 변경하지 않는다.

### 3. 목 데이터 삽입

```bash
cd /path/to/market-mvp
python scripts/seed_mock.py
```

`INSERT IGNORE` 방식이므로 중복 실행해도 안전하다.

---

## 테스트 계정

| email | password | role |
|---|---|---|
| consumer01@market.com | password123 | consumer |
| consumer02@market.com | password123 | consumer |
| merchant01@market.com | password123 | merchant |
| merchant02@market.com | password123 | merchant |
| operator01@market.com | password123 | operator |

- 비밀번호는 `seed_mock.py` 실행 시 bcrypt (rounds=12) 로 해싱되어 저장된다.
- `operator` 계정은 DB에 존재하지만 MVP API에서는 비활성 상태다.

---

## 파일 목록

| 파일 | 테이블 | 건수 |
|---|---|---|
| markets.json | Market | 1 |
| users.json | User | 5 |
| stores.json | Store | - |
| merchants.json | Merchant | - |
| products.json | Product | - |
| drop_events.json | DropEvent | - |
| catalog_items.json | CatalogItem | - |
| shopping_lists.json | ShoppingList | - |
| shopping_list_items.json | ShoppingListItem | - |
| route_plans.json | RoutePlan | - |
| notifications.json | Notification | - |
| preorders.json | Preorder | - |
