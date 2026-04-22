# Phase 2 코드 리뷰 & 배포 — Claude Code 작업 지시서

## 컨텍스트

Market Info MVP 프로젝트.
- 백엔드: FastAPI + SQLAlchemy + MySQL 8.0 (`server/` 폴더)
- 배포: Railway (`https://market-api-production-6e52.up.railway.app`)
- DB: Railway MySQL (`market_mvp`)

Day 1~4 기존 코드(72 tests)는 정상 동작 중.
**Phase 2 신규 코드가 작성되어 있다. 지금부터 리뷰 → 수정 → 배포를 진행한다.**

---

## Phase 2에서 추가된 파일 목록

```
server/app/db/models/
  market_price.py          # MarketPrice, ProductPriceHistory 모델
  preorder.py              # Preorder 모델 (schema.sql과 1:1)

server/app/db/repositories/
  price_repository.py      # MarketPrice / ProductPriceHistory CRUD
  preorder_repository.py   # Preorder CRUD

server/app/services/
  price_service.py         # KAMIS 연동, 가격 자동 업데이트, 대시보드 제안 문구
  story_service.py         # LLM 스토리 생성 (Anthropic Claude, fallback 포함)
  preorder_service.py      # Preorder 상태 전이 + Notification 자동 생성

server/app/api/v1/
  prices.py                # 가격 API 라우터
  stories.py               # 스토리 생성 API 라우터
  preorders.py             # Preorder API 라우터

server/tests/
  test_prices.py           # 13 tests
  test_stories.py          # 9 tests
  test_preorders.py        # 14 tests

db/schema.sql              # MarketPrice, ProductPriceHistory 테이블 정의 추가됨
```

`server/app/db/models/__init__.py` — 새 모델 import 추가됨  
`server/app/api/v1/router.py` — prices, stories, preorders 라우터 등록됨  
`server/app/services/merchant_service.py` — `get_price_suggestions()` 추가됨

---

## 신규 API 엔드포인트 목록

| Method | Path | 권한 | 설명 |
|--------|------|------|------|
| GET    | `/api/v1/prices/market/{kamis_item_code}` | 공개 | 최신 KAMIS 시세 조회 |
| POST   | `/api/v1/prices/market/{kamis_item_code}/sync` | 로그인 | KAMIS 시세 동기화 |
| POST   | `/api/v1/merchant/products/{product_id}/price` | merchant | KAMIS 기반 상품 가격 자동 업데이트 |
| GET    | `/api/v1/merchant/products/{product_id}/price-history` | merchant | 가격 변경 이력 |
| GET    | `/api/v1/merchant/dashboard/price-suggestions` | merchant | 가격 정책 보조 문구 |
| POST   | `/api/v1/merchant/stories` | merchant | LLM 스토리 생성 |
| POST   | `/api/v1/preorders` | 로그인 | 사전 주문 생성 |
| GET    | `/api/v1/preorders` | 로그인 | 내 사전 주문 목록 |
| PATCH  | `/api/v1/merchant/preorders/{preorder_id}/status` | merchant | 상태 변경 + 알림 |

---

## 리뷰 체크리스트 (순서대로 진행)

### Step 1 — 로컬 테스트 실행

```bash
cd server
DATABASE_URL="sqlite:////tmp/test_phase2.db" SECRET_KEY="testsecret" \
  pytest tests/test_prices.py tests/test_stories.py tests/test_preorders.py -v
```

기대 결과: **36 passed, 0 failed**

### Step 2 — 기존 테스트 회귀 확인

```bash
# 기존 테스트는 Railway DB 연결이 필요한 것들이 있으니
# SQLite로 돌릴 수 있는 것만 확인
DATABASE_URL="sqlite:////tmp/test_phase2.db" SECRET_KEY="testsecret" \
  pytest tests/test_common.py tests/test_security.py -v
```

### Step 3 — 코드 리뷰 포인트

아래 항목들을 검토하고 필요하면 수정한다:

1. **`price_service.py`의 KAMIS 품목 코드 매핑** (`KAMIS_ITEM_MAP`)  
   - 현재 7개 품목만 하드코딩 — 추가 품목 필요하면 보완

2. **`preorder_service.py`의 상태 전이 규칙** (`_VALID_TRANSITIONS`)  
   - `requested → confirmed → ready → cancelled` 구조 확인

3. **`story_service.py`의 LLM 모델**  
   - 현재 `claude-haiku-4-5-20251001` 사용 중 — 변경 필요 시 수정

4. **`merchant_service.py`의 대시보드**  
   - `get_price_suggestions` 추가됨 — 기존 `get_dashboard` 응답에 포함할지 별도 엔드포인트로 둘지 결정

### Step 4 — Railway DB 마이그레이션

신규 테이블 2개를 Railway MySQL에 생성해야 함:

```bash
# Railway CLI 또는 DB 콘솔에서 실행
# db/schema.sql 에 추가된 CREATE TABLE 두 개를 Railway DB에 반영

railway connect  # 또는 MySQL 클라이언트로 직접 접속
```

적용할 DDL은 `db/schema.sql`의 `MarketPrice`와 `ProductPriceHistory` 부분.

```sql
-- 이 두 블록만 Railway DB에 실행
CREATE TABLE IF NOT EXISTS `MarketPrice` ( ... );
CREATE TABLE IF NOT EXISTS `ProductPriceHistory` ( ... );
```

`Preorder` 테이블은 기존에 이미 존재함 — 스킵.

### Step 5 — 환경변수 확인 (Railway)

Railway 대시보드 또는 CLI에서 아래 변수 추가 여부 확인:

| 변수 | 설명 | 필수 |
|------|------|------|
| `KAMIS_API_KEY` | KAMIS 농산물 API 인증키 | 선택 (없으면 fallback) |
| `KAMIS_API_ID` | KAMIS 신청자 ID | 선택 |
| `ANTHROPIC_API_KEY` | Claude API 키 (스토리 생성) | 선택 (없으면 fallback) |

```bash
railway variables set KAMIS_API_KEY=your_key
railway variables set ANTHROPIC_API_KEY=your_key
```

### Step 6 — Railway 배포

```bash
cd server   # 또는 프로젝트 루트
git add .
git commit -m "feat: Phase 2 — KAMIS 가격 연동, 스토리 생성, Preorder 플로우"
git push origin main   # Railway 자동 배포 트리거
```

### Step 7 — 배포 후 스모크 테스트

```bash
BASE="https://market-api-production-6e52.up.railway.app/api/v1"

# 1. 헬스 체크
curl $BASE/../health

# 2. KAMIS 시세 조회 (214 = 사과/후지)
curl "$BASE/prices/market/214"

# 3. 사전 주문 생성 (토큰 필요)
TOKEN=$(curl -s -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"consumer@example.com","password":"test1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

curl -X POST $BASE/preorders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"store_id":"<실제store_id>","product_name":"딸기","qty":2}'
```

---

## 공통 응답 구조 (변경 없음)

```json
{
  "success": true,
  "code": "OK",
  "message": "요청이 성공했습니다.",
  "data": {},
  "meta": { "request_id": "req_xxx", "timestamp": "..." }
}
```

---

## 참고: Preorder 상태 전이 규칙

```
requested ──→ confirmed ──→ ready
    │               │          │
    └───────────────┴──────────┴──→ cancelled
```

상태 변경 시 자동 Notification 생성:
- `confirmed` → "사전 주문 확인됨"
- `ready` → "상품 준비 완료"
- `cancelled` → "주문 취소됨"
