# API Specification — 프론트엔드 최종 계약서

## 0. 문서 정보
- 문서명: **Market Info API 계약서 (Phase 2 최종)**
- 버전: **v2.0**
- 작성일: **2026-05-11**
- 상태: **프론트엔드 연동 계약서 확정 — 이후 breaking change 금지**
- Base URL: `/api/v1`
- 배포 URL: `https://market-api-production-6e52.up.railway.app`
- OpenAPI(Swagger UI): `https://market-api-production-6e52.up.railway.app/docs`
- OpenAPI JSON: `https://market-api-production-6e52.up.railway.app/openapi.json`
- 기준 문서: `docs/SPEC.md`, `docs/Fuctional_Specification.md`, `docs/UIUX_Speification.md`, `docs/ERD.md`

---

## 1. 공통 규약

### 1.1 Header
- `Content-Type: application/json`
- `Authorization: Bearer {access_token}` (로그인 이후 모든 보호 엔드포인트)

### 1.2 공통 응답 (모든 엔드포인트 통일)
```json
{
  "success": true,
  "code": "OK",
  "message": "요청이 성공했습니다.",
  "data": { /* 엔드포인트별 페이로드 */ },
  "meta": {
    "request_id": "req_a1b2c3d4",
    "timestamp": "2026-05-11T10:00:00+00:00"
  }
}
```

### 1.3 에러 응답 (공통 핸들러 적용 — `app/core/exceptions.py`)
```json
{
  "success": false,
  "code": "FORBIDDEN",
  "message": "본인 점포 스토리만 관리할 수 있습니다.",
  "data": null,
  "meta": { "request_id": "req_xxx", "timestamp": "..." }
}
```

| HTTP | code 값 | 설명 |
|---|---|---|
| 400 | `BAD_REQUEST` | 잘못된 요청 (예: 지원하지 않는 KAMIS 품목코드) |
| 401 | `UNAUTHORIZED` | 토큰 없음/만료 |
| 403 | `FORBIDDEN` | 권한 없음 (다른 점포 자원 접근 등) |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 409 | `CONFLICT` | 상태 충돌 (드랍 동일 상태 재설정, preorder 잘못된 전이 등) |
| 422 | `VALIDATION_ERROR` | Pydantic 입력 검증 실패 |
| 500 | `INTERNAL_ERROR` | 서버 오류 |
| 503 | `AI_UNAVAILABLE` | KAMIS/Anthropic 등 외부 API 데이터 부재 |

### 1.4 페이지네이션 규약
- Query: `page`(default 1, ≥1), `size`(default 20, 1~100)
- 응답에 다음 객체 포함:
  ```json
  "pagination": { "page": 1, "size": 20, "total": 42, "has_next": true }
  ```
- 적용 엔드포인트: `/drops`, `/products/search`, `/notifications`, `/preorders`, `/merchant/stories`

### 1.5 타임존/날짜
- 모든 datetime: **ISO-8601 UTC** (예: `2026-05-11T10:00:00+00:00`)
- 가격 이력 등 시계열: **일 단위**, `created_at.desc()` 정렬 (최신순)
- 프론트는 사용자 표시 직전 KST(`Asia/Seoul`)로 변환

### 1.6 권한 매트릭스
| 자원 | consumer | merchant | operator |
|---|---|---|---|
| 본인 점포 외 상품 수정 | — | 403 | — |
| 다른 상인 스토리 수정 | — | 403 | — |
| 비공개·미게시 스토리 소비자 조회 | 빈 객체 `{}` | (본인 점포 한해) 200 | — |
| 다른 점포 드랍 상태 변경 | — | 403 | — |
| 다른 사용자 preorder 단건 조회 | 403 | 403 (담당 점포 외) | — |

---

## 2. 인증 API

### 2.1 로그인
- **`POST /api/v1/auth/login`** (공개)
- Request: `{ "email": "consumer01@market.com", "password": "password123" }`
- Response `data`:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "user_id": "a1b2c3d4-...",
    "email": "consumer01@market.com",
    "role": "consumer",
    "name": "김지연"
  }
}
```

### 2.2 내 정보
- **`GET /api/v1/auth/me`** (🔒)
- Response `data`: `{ user_id, email, role, name }`

---

## 3. 홈/이벤트/검색

### 3.1 홈 피드
- **`GET /api/v1/home?market_id={market_id}`** (공개)
- Response `data`:
```json
{
  "market": { "market_id": "f1a2b3c4-...", "market_name": "망원시장" },
  "drop_hero": [
    { "drop_id": "...", "product_id": "...", "store_id": "...",
      "title": "...", "image_url": "...", "status": "scheduled",
      "expected_at": "2026-05-12T08:00:00+00:00" }
  ],
  "event_cards":      [ { "catalog_item_id": "...", "title": "...", "image_url": "..." } ],
  "store_spotlights": [ { "store_id": "...", "store_name": "...", "summary": "...", "image_url": "..." } ]
}
```

### 3.2 이벤트 상세
- **`GET /api/v1/events/{catalog_item_id}`** (공개)

### 3.3 상품 검색
- **`GET /api/v1/products/search`** (공개)
- Query: `q` (필수), `market_id?`, `sort=price_asc|latest`, `stock_status=in_stock|low_stock|out_of_stock`, `page`, `size`
- Response: `{ items: [...], pagination: {...} }`

### 3.4 상품 상세
- **`GET /api/v1/products/{product_id}`** (공개)

---

## 4. 드랍 API

### 4.1 드랍 리스트
- **`GET /api/v1/drops?market_id=&status=&page=&size=`** (선택 인증 — 로그인 시 `is_subscribed` 포함)
- Response `data.items[*]`:
```json
{
  "drop_id":"dr000001-...", "product_id":"p1000001-...",
  "product_name":"국내산 시금치 200g",
  "store_id":"d1000003-...", "store_name":"망원 과일나라",
  "expected_at":"2026-05-12T08:00:00+00:00",
  "status":"scheduled", "is_subscribed":false
}
```

### 4.2 드랍 구독 / 해제
- **`POST /api/v1/drops/{drop_id}/subscribe`** (🔒)
- **`DELETE /api/v1/drops/{drop_id}/subscribe`** (🔒)

---

## 5. 점포 API

### 5.1 점포 스포트라이트
- **`GET /api/v1/stores/{store_id}/spotlight`** (공개)

### 5.2 점포 상품 목록
- **`GET /api/v1/stores/{store_id}/products`** (공개)
- Response: `{ items: [{ product_id, product_name, price, stock_status, category, image_url }] }`

### 5.3 점포 스토리(소비자용) **[신규]**
- **`GET /api/v1/stores/{store_id}/story`** (공개)
- 게시된 최신 스토리 1건만 반환. **없거나 미게시 시 `data: {}`** (200 OK, 404 아님)
- Response `data` (게시 있을 때):
```json
{
  "story_id":"st000001-...", "store_id":"d1000001-...", "merchant_id":"e1000001-...",
  "title":null,
  "content":"신선한 채소를 매일 새벽 망원시장으로 가져옵니다.",
  "story_versions":{ "short":"...", "normal":"...", "detailed":"..." },
  "tone":"친근한", "selected_length":"normal",
  "hashtags":["#망원시장","#신선야채"],
  "interview_text":null, "fallback_mode":false,
  "is_published":true, "published_at":"2026-05-10T11:30:00+00:00",
  "created_at":"2026-05-10T11:30:00+00:00", "updated_at":null
}
```

---

## 6. 상인 스토리 API (Phase 2 신규)

### 6.1 스토리 생성 (LLM)
- **`POST /api/v1/merchant/stories`** (🔒 merchant)
- Request:
```json
{
  "store_id":"d1000001-...",
  "save_to_store": false,
  "interview_text":"30년 동안 새벽시장에서...",
  "keywords":["새벽","신선","제철"],
  "tone":"친근한",
  "selected_length":"normal",
  "publish": true,
  "persist": true
}
```
- 필드 가능 값:
  - `tone`: `친근한 | 전문적인 | 정겨운` (default `친근한`)
  - `selected_length`: `short | normal | detailed` (default `normal`)
  - `publish`: 생성과 동시에 게시 여부 (default false)
  - `persist`: Story 테이블 저장 여부 (default true)
- Response `data`:
```json
{
  "store_id":"d1000001-...", "store_name":"망원 신선야채",
  "story_id":"st000099-...",          // persist=false면 null
  "story":"친근하고 알기 쉬운 설명으로 ...",
  "story_versions": { "short":"...", "normal":"...", "detailed":"..." },
  "selected_length":"normal", "tone":"친근한",
  "hashtags":["#새벽","#신선","#제철","#시금치","#감자"],
  "interview_masked":"30년 동안 새벽시장에서...",
  "fallback_mode": false,
  "is_published": true,
  "published_at":"2026-05-11T10:00:00+00:00",  // publish=false면 null
  "created_at":"2026-05-11T10:00:00+00:00",
  "products_used":["국내산 시금치 200g","강원도 감자 1kg",...]
}
```
- **에러**: 403(상인 권한 없음), 404(점포 없음/연결된 점포 없음)
- **fallback**: `ANTHROPIC_API_KEY` 미설정 또는 LLM 호출 실패 시 `fallback_mode:true`, 템플릿 문구 반환

### 6.2 본인 스토리 목록
- **`GET /api/v1/merchant/stories?page=1&size=20`** (🔒 merchant)
- 정렬: **게시 우선 → 최신순** (`is_published DESC, created_at DESC`)
- Response `data`:
```json
{
  "items":[ /* 6.4와 동일한 story 객체 */ ],
  "pagination":{ "page":1,"size":20,"total":42,"has_next":true }
}
```

### 6.3 스토리 단건
- **`GET /api/v1/merchant/stories/{story_id}`** (🔒 merchant)
- Response: 6.4와 동일한 story 객체

### 6.4 스토리 수정
- **`PATCH /api/v1/merchant/stories/{story_id}`** (🔒 merchant, 본인 점포)
- Request: `{ "selected_length":"detailed", "title":"새 제목" }` (모두 optional)
- Response: 업데이트된 **전체 story 객체** (`to_dict()` 결과 그대로)

### 6.5 게시 토글
- **`PATCH /api/v1/merchant/stories/{story_id}/publish`** (🔒 merchant, 본인 점포)
- Request: `{ "publish": true }` (false 시 게시 해제 + `published_at=null`)
- Response: 업데이트된 **전체 story 객체** (포함 필드: `is_published`, `published_at`, `updated_at`)

### 6.6 스토리 삭제 (soft delete)
- **`DELETE /api/v1/merchant/stories/{story_id}`** (🔒 merchant, 본인 점포)
- `deleted_at` 설정 + `is_published=0` 자동 해제. 목록/조회에서 즉시 제외.
- Response `data`: `{ "story_id": "...", "deleted": true }`

---

## 7. 가격 정책 / 시세 API (Phase 2 신규)

### 7.1 KAMIS 시세 조회
- **`GET /api/v1/prices/market/{kamis_item_code}`** (공개)
- Response `data`:
```json
{
  "market_price_id":"mp000001-...",
  "item_name":"배추/포기", "kamis_item_code":"112", "unit":"1포기",
  "price_date":"2026-05-11",
  "retail_price":4500,
  "prev_day_price":4300, "prev_month_price":4100, "prev_year_price":3800,
  "fallback_mode":false
}
```
- **에러**: 404 `시세 데이터가 없습니다. 먼저 sync를 실행하세요.`

### 7.2 KAMIS 시세 동기화
- **`POST /api/v1/prices/market/{kamis_item_code}/sync`** (🔒)
- 외부 KAMIS API 호출 → 저장 → 반환. `KAMIS_API_KEY` 미설정 시 `fallback_mode:true`로 DB 최신값 반환.
- Response: 7.1과 동일 구조

### 7.3 상품 가격 KAMIS 자동 업데이트
- **`POST /api/v1/merchant/products/{product_id}/price?kamis_item_code=112`** (🔒 merchant, 본인 점포 상품)
- `ProductPriceHistory`에 자동 기록 (`reason:"kamis"`)
- Response `data`:
```json
{
  "product_id":"p1000001-...",
  "old_price":4000, "new_price":4500,
  "kamis_item_code":"112", "price_date":"2026-05-11",
  "fallback_mode":false
}
```
- **에러**: 403(본인 점포 아님), 404(상품 없음), 503(시세 데이터 없어 업데이트 불가)

### 7.4 상품 가격 이력
- **`GET /api/v1/merchant/products/{product_id}/price-history?limit=30`** (🔒 merchant, 본인 점포 상품)
- 정렬: **created_at DESC** (최신순)
- Response `data`:
```json
{
  "product_id":"p1000001-...",
  "items":[
    {
      "history_id":"...",
      "old_price":4000, "new_price":4500,
      "change_amount":500, "change_rate":12.5,
      "reason":"kamis",          // manual | kamis | admin
      "reference_id":"mp000001-...",  // MarketPrice id (manual은 null)
      "created_at":"2026-05-11T10:00:00+00:00"
    }
  ]
}
```

### 7.5 가격 정책 보조 문구 (대시보드)
- **`GET /api/v1/merchant/dashboard/price-suggestions`** (🔒 merchant)
- 매칭 규칙:
  1. `PRODUCT_KAMIS_KEYWORDS` 사전(2자 이상 키워드) 우선 매칭
  2. 폴백으로 `KAMIS_ITEM_MAP.item_name` 접두 매칭
- `diff_pct` = `(현재가 − KAMIS 소매가) / KAMIS 소매가 × 100`, 소수 1자리
- 임계값: `diff_pct > 10` 인하 권장, `< -10` 인상 여지, 그 외 적정
- Response `data`:
```json
{
  "suggestions":[
    {
      "product_id":"...", "product_name":"국내산 시금치 200g",
      "current_price":2500, "market_price":2300,
      "price_date":"2026-05-11", "diff_pct":8.7,
      "advice":"현재 가격이 시세와 유사합니다 (±8.7%)."
    }
  ]
}
```
- KAMIS 매칭 실패 상품은 응답에서 제외 (suggestions 길이 < 상품 수 가능)

### 7.6 지원 KAMIS 품목코드 (30품목)
| 코드 | 품목 | 단위 |
|---|---|---|
| 112,151~157 | 배추/무/당근/양파/대파/마늘/청양고추/시금치 | 채소 8 |
| 214~219, 421, 422 | 사과/배/감귤/샤인머스캣/딸기/수박/단감/복숭아 | 과일 8 |
| 601~607 | 고등어/갈치/오징어/꽃게/새우/광어회/굴 | 수산물 7 |
| 501~507 | 한우등심/한우갈비/삼겹살/목살/닭다리/닭가슴/불고기 | 육류 7 |

> 전체 매핑은 `server/app/services/price_service.py:KAMIS_ITEM_MAP` 참고.

---

## 8. Preorder API (Phase 2 신규)

### 8.1 생성
- **`POST /api/v1/preorders`** (🔒 consumer/merchant)
- Request: `{ "store_id":"...", "product_name":"단감", "qty":2 }`

### 8.2 목록
- **`GET /api/v1/preorders?status=&page=&size=`** (🔒)
- `consumer`는 본인 / `merchant`는 담당 점포 전체
- `status` 필터: `requested | confirmed | ready | cancelled`
- Response: `{ items:[...], pagination:{...} }`

### 8.3 단건
- **`GET /api/v1/preorders/{preorder_id}`** (🔒, 권한 외 403)

### 8.4 소비자 취소
- **`DELETE /api/v1/preorders/{preorder_id}`** (🔒 consumer, requested 상태만 — 그 외 409)

### 8.5 상인 상태 변경
- **`PATCH /api/v1/merchant/preorders/{preorder_id}/status`** (🔒 merchant)
- Request: `{ "status":"confirmed" }`
- 허용 전이: `requested→confirmed|cancelled`, `confirmed→ready|cancelled`, `ready→cancelled`, 그 외 409
- 상태 변경 시 주문자에게 Notification 자동 생성

### 8.6 Preorder 객체 공통 필드
```json
{
  "preorder_id":"...", "user_id":"...",
  "store_id":"d1000001-...", "store_name":"망원 신선야채",
  "product_name":"단감", "qty":2,
  "status":"requested",
  "created_at":"2026-05-11T10:00:00+00:00"
}
```

---

## 9. Shopping Agent API (Phase 2 신규)

### 9.1 추천 생성
- **`POST /api/v1/shopping-agent/recommendations`** (🔒)
- Request:
```json
{
  "query":"오늘 저녁 찌개 추천해줘",
  "people":2, "budget":15000,
  "preferences":["매운맛"],
  "market_id":"f1a2b3c4-...",
  "save_as_list":true
}
```
- Response `data`:
```json
{
  "query":"오늘 저녁 찌개 추천해줘",
  "clarification_needed":false, "clarification_question":null,
  "stage":"menu_list_matching",
  "menu":{ "title":"제철 고추장찌개 세트","reason":"...","rag_source":"sample_recipe_dataset_v1","people":2,"budget":15000 },
  "ingredients":[
    { "name":"돼지고기","qty":300,"unit":"g","seasonal":false,
      "alternatives":["소고기","두부"],
      "match_status":"matched", "substituted_with":null,
      "matched_store":{ "store_id":"...","store_name":"...","zone_label":"A구역","price":4500,"stock_status":"in_stock" } }
  ],
  "store_matches":[
    { "store_id":"...","store_name":"...","zone_label":"A구역",
      "distance_m":120,"matched_items":["돼지고기","대파"],
      "price_total":6000, "stock_priority":"in_stock" }
  ],
  "matching_failed":false, "general_list_only":false,
  "shopping_list_id":"sl-...",   // save_as_list=true 시
  "fallback_mode":false, "retry_guide":null
}
```
- **모호 질의 시**: `clarification_needed:true`, `stage:"clarification"`, `clarification_question` 반환
- **fallback**: 일시 오류 시 기본 추천 템플릿 + `fallback_mode:true`

---

## 10. 장보기 리스트 API (기존)

| 메서드 | 경로 | 인증 | 비고 |
|---|---|---|---|
| GET    | `/shopping-lists` | 🔒 | 본인 리스트 |
| POST   | `/shopping-lists` | 🔒 | body: `{ title }` |
| POST   | `/shopping-lists/{shopping_list_id}/items` | 🔒 | body: `{ product_name_snapshot, qty, unit, product_id?, estimated_price?, store_id? }` |
| PATCH  | `/shopping-lists/{shopping_list_id}/items/{list_item_id}` | 🔒 | body: `{ checked?, qty? }` |
| DELETE | `/shopping-lists/{shopping_list_id}/items/{list_item_id}` | 🔒 | |

---

## 11. 동선 API (기존)

| 메서드 | 경로 | 인증 | 비고 |
|---|---|---|---|
| POST | `/routes/plans`               | 🔒 | body: `{ market_id, shopping_list_id }` |
| GET  | `/routes/plans/{route_plan_id}` | 🔒 | `route_json` + `zone_label` |

---

## 12. 알림 API (기존)

| 메서드 | 경로 | 인증 | 비고 |
|---|---|---|---|
| GET   | `/notifications?is_read=0|1&page=&size=` | 🔒 | 페이지네이션 적용 |
| PATCH | `/notifications/{notification_id}/read`  | 🔒 | |

---

## 13. 상인 일반 API

| 메서드 | 경로 | 인증 | 비고 |
|---|---|---|---|
| GET    | `/merchant/dashboard` | 🔒 merchant | `today_product_count, risk_stock_count, pending_request_count, today_drop_count` |
| GET    | `/merchant/my-store`  | 🔒 merchant | `{ store_id, store_name, zone_label, market_id }` |
| POST   | `/merchant/products`  | 🔒 merchant | 상품 등록 |
| POST   | `/merchant/products/ai-draft` | 🔒 merchant | AI 초안. fallback_mode 포함 |
| PATCH  | `/merchant/products/{product_id}` | 🔒 merchant | `{ price?, stock_status? }`. 가격 변경 시 PriceHistory 자동 기록(`reason:manual`) |
| PATCH  | `/merchant/drops/{drop_id}/status` | 🔒 merchant | `{ status }`. 동일 상태 재설정 시 409 |

---

## 14. 시드/환경

### 14.1 테스트 계정 (Railway, 비밀번호 전부 `password123`)
| 역할 | 이메일 | 비고 |
|---|---|---|
| consumer | `consumer01@market.com` ~ `consumer04@market.com` | 일반 사용자 |
| merchant | `merchant01@market.com`, `merchant02@market.com` | 상인 |
| operator | `operator01@market.com` | (현재 API 비활성) |

### 14.2 시드 건수 (mock_v2)
| 테이블 | 건수 |
|---|---|
| User | 50 |
| Market | 11 |
| Store | 101 |
| Product | 497 |
| DropEvent | 120 |
| MarketPrice | 900 |
| ProductPriceHistory | 303 |
| Story | 207 (+ LLM 시드 stories_llm.json 1,227건) |

### 14.3 Fallback 강제 테스트
- Railway 환경변수에서 `ANTHROPIC_API_KEY` 제거 → `POST /merchant/stories` 응답 `fallback_mode:true`
- Railway 환경변수에서 `KAMIS_API_KEY` 제거 → `POST /prices/market/{code}/sync` 응답 `fallback_mode:true`
- 로컬 재현: `server/.env`에서 해당 키 주석 처리 후 `uvicorn app.main:app --reload`

---

## 15. 변경 관리
1. 필드 **추가**(optional)는 언제든 허용
2. 필드 **삭제/타입 변경/경로 변경**은 **v2**(`/api/v2`)에서만 — 기존 v1 응답 깨기 금지
3. 변경 시 PR에 프론트/백엔드 동시 승인 필요
4. ENUM 값 추가도 신중히: 프론트가 모르는 값 들어오면 표시 깨질 수 있음

---

## 16. 부속 자료
- 화면별 추천 샘플 ID: `docs/sample_ids.md`
- Postman 컬렉션: `docs/postman_collection.json`
- 실시간 OpenAPI: 위 0번의 `/docs`, `/openapi.json`
