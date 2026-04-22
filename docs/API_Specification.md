# API Specification (MVP Contract)

## 1. 문서 정보
- 문서명: Market Info API 명세서
- 버전: v1.2
- 작성일: 2026-04-21
- Base URL: `/api/v1`
- 기준 문서
1. `project/docs/Fuctional_Specification.md`
2. `project/docs/UIUX_Speification.md`
3. `project/docs/ERD.md`
4. `project/docs/db_setup_report.md`

## 2. 공통 규약
### 2.1 Header
- `Content-Type: application/json`
- `Authorization: Bearer {access_token}` (로그인 이후)

### 2.2 공통 응답
```json
{
  "success": true,
  "code": "OK",
  "message": "요청이 성공했습니다.",
  "data": {},
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-04-21T10:00:00+09:00"
  }
}
```

### 2.3 에러 코드
| HTTP | code | 설명 |
|---|---|---|
| 400 | BAD_REQUEST | 잘못된 요청 |
| 401 | UNAUTHORIZED | 인증 실패 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 상태 충돌 |
| 422 | VALIDATION_ERROR | 입력 검증 실패 |
| 500 | INTERNAL_ERROR | 서버 오류 |
| 503 | AI_UNAVAILABLE | AI 서비스 불가 |

### 2.4 페이지네이션
- Query: `page`(기본 1), `size`(기본 20, 최대 100)
- 응답: `pagination.page`, `pagination.size`, `pagination.total`, `pagination.has_next`

## 3. 인증 API
### 3.1 로그인
- `POST /auth/login`
- 인증 방식: 이메일/비밀번호 + JWT (MVP 시연용 / 소셜 로그인은 MVP 이후 추가)
- Request
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- Response `data`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "user_consumer_001",
    "email": "user@example.com",
    "role": "consumer",
    "name": "홍길동"
  },
  "home_screen_id": "SCR-C-01"
}
```

### 3.2 내 정보
- `GET /auth/me`
- `Authorization: Bearer {access_token}` 헤더에서 user 정보 추출

## 4. 홈 허브 API (SCR-C-01)
### 4.1 홈 피드 조회
- `GET /home`
- Query: `market_id`(optional)
- 로그인 사용자의 경우 `user_id`는 JWT에서 추출
- Response `data`
```json
{
  "market": {
    "market_id": "market_001",
    "market_name": "망원시장"
  },
  "drop_hero": [
    {
      "drop_id": "drop_001",
      "product_id": "product_001",
      "store_id": "store_001",
      "title": "하동에서 온 꿀맛 단감",
      "image_url": "https://...",
      "status": "scheduled",
      "expected_at": "2026-04-21T08:00:00+09:00"
    }
  ],
  "event_cards": [
    {
      "catalog_item_id": "catalog_001",
      "title": "전통시장 이벤트",
      "image_url": "https://..."
    }
  ],
  "store_spotlights": [
    {
      "store_id": "store_003",
      "store_name": "청정 채소점",
      "summary": "오늘의 추천 점포",
      "image_url": "https://..."
    }
  ]
}
```

## 5. 검색/상품 API
### 5.1 상품 검색/비교 (SCR-C-02)
- `GET /products/search`
- Query
1. `q` (required)
2. `market_id` (optional)
3. `sort=price_asc|latest`
4. `stock_status=in_stock|low_stock|out_of_stock`
5. `page`, `size`

### 5.2 상품 상세 (SCR-C-03)
- `GET /products/{product_id}`
- Response는 상품 + 점포(구역 포함) 반환

## 6. 드랍 API (핵심)
드랍은 MVP 핵심 기능이며 방문 트리거로 우선 구현한다.

### 6.1 드랍 리스트 (SCR-C-04)
- `GET /drops`
- Query: `market_id`(optional), `status`(optional), `page`, `size`
- `status`: `scheduled|arrived|sold_out`
- UI 라벨 매핑
1. `scheduled` → 예정
2. `arrived` → 확정/도착
3. `sold_out` → 마감/품절
- Response `data.items[*]`
```json
{
  "drop_id": "drop_001",
  "product_id": "product_001",
  "product_name": "단감",
  "store_id": "store_001",
  "store_name": "망원 과일나라",
  "expected_at": "2026-04-21T08:00:00+09:00",
  "status": "scheduled",
  "is_subscribed": false
}
```

### 6.2 드랍 구독
- `POST /drops/{drop_id}/subscribe`
- `user_id`는 JWT에서 추출 (별도 Request body 불필요)

### 6.3 드랍 구독 취소
- `DELETE /drops/{drop_id}/subscribe`
- `user_id`는 JWT에서 추출 (별도 Query 파라미터 불필요)

## 7. 장보기 리스트 API (SCR-C-06)
### 7.1 리스트 조회
- `GET /shopping-lists`
- `user_id`는 JWT에서 추출

### 7.2 리스트 생성
- `POST /shopping-lists`
- `user_id`는 JWT에서 추출

### 7.3 리스트 아이템 추가
- `POST /shopping-lists/{shopping_list_id}/items`
- Request 필수: `product_name_snapshot`, `qty`, `unit`

### 7.4 리스트 아이템 체크 변경
- `PATCH /shopping-lists/{shopping_list_id}/items/{list_item_id}`

### 7.5 리스트 아이템 삭제
- `DELETE /shopping-lists/{shopping_list_id}/items/{list_item_id}`

## 8. 동선 API (SCR-C-07)
### 8.1 동선 생성
- `POST /routes/plans`
- Request 필수: `market_id`, `shopping_list_id`
- `user_id`는 JWT에서 추출

### 8.2 동선 조회
- `GET /routes/plans/{route_plan_id}`
- `route_json` 원본 반환 + `zone_label` 기반 안내 포함

## 9. 알림 API (SCR-C-09)
### 9.1 알림 목록
- `GET /notifications?is_read={0|1}&page=1&size=20`
- `user_id`는 JWT에서 추출
- 핵심 필드: `type`, `target_type`, `target_id`, `is_read`

### 9.2 읽음 처리
- `PATCH /notifications/{notification_id}/read`

## 10. 상인 API (SCR-M-01/02/03)
### 10.1 상인 홈 요약
- `GET /merchant/dashboard`
- `user_id`는 JWT에서 추출
- 응답: `today_product_count`, `risk_stock_count`, `pending_request_count`, `today_drop_count`

### 10.2 상품 등록 (수동)
- `POST /merchant/products`
- Request 필수: `store_id`, `product_name`, `price`, `stock_status`
- merchant 권한 검증은 JWT의 `role` 필드로 수행

### 10.3 상품 등록 AI draft
- `POST /merchant/products/ai-draft`
- Request: `store_id`, `image_url`(optional), `voice_text`(optional)
- Response: `draft.product_name`, `draft.category`, `draft.description`, `fallback_mode`

## 11. DB 컬럼/엔터티 매핑 고정
1. `Product.stock_status` 사용 (`in_stock|low_stock|out_of_stock`)
2. `DropEvent.status` 사용 (`scheduled|arrived|sold_out`)
3. `Notification.target_type + target_id` 필수
4. `ShoppingListItem.unit` 필수
5. `RoutePlan.route_json` 필수
6. `User.role`의 `operator`는 DB 유지, MVP API는 비활성

## 12. 비활성/Phase 정책
1. Preorder API는 현재 비활성 (DB만 존재)
2. 운영자 전용 API는 현재 비활성
3. 결제/정산 API는 현재 미구현

## 13. 변경관리
1. 필드 추가는 optional만 허용
2. breaking change는 `v2`에서만 반영
3. 변경 시 프론트/백엔드 동시 승인
