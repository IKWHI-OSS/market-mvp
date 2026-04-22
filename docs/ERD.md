# ERD (MVP Prototype)

## 1. 문서 정보

- 문서명: Market Info 데이터 구조도 초안 (ERD)
- 버전: v0.9 (MVP 개발 착수용)
- 작성일: 2026-04-18
- 작성자: 박래윤
- 연계 문서
1. `docs/Fuctional_Specification.md`
2. `docs/UIUX_Speification.md`
- 목적: 시연 가능한 MVP 구현을 위한 실무형 데이터 구조 정의

## 2. 데이터 구조 설계 원칙

1. MVP 우선 단순화
- 검색/비교, 드랍, 카탈로그, 장보기 리스트, 지도/동선, 상인 등록에 직접 필요한 필드만 정의한다.
- 고도화 분석용 필드와 정규화는 최소화한다.

2. 데이터 출처 분리
- 공공데이터/API와 모킹데이터를 엔터티 단위로 명시한다.
- 시연 안정성을 위해 핵심 사용자 경험은 모킹데이터로 제어한다.

3. 확장 가능한 구조 유지
- 실서비스 전환 시 분리 가능한 엔터티는 `Merchant`, `Inventory`, `PriceHistory`, `Story`다.
- MVP에서는 `Store` 중심으로 통합하고, 향후 단계에서 분리한다.

4. 과설계 금지
- 운영형 결제/정산/회계/복잡 권한은 제외한다.
- MVP 기준으로 읽기 쉬운 구조를 우선한다.

## 3. 핵심 엔터티 목록 (확정)

| 엔터티 | MVP 포함 | Phase | 핵심 기능 연결 | 데이터 출처 기본값 |
|---|---|---|---|---|
| User | 포함 | MVP | 장보기 리스트, 알림 | 모킹 |
| Market | 포함 | MVP | 시장 탐색, 지도 | 공공/API + 모킹 보정 |
| Store | 포함 | MVP | 검색/비교, 지도, 카탈로그 | 공공/API + 모킹 보정 |
| Merchant | 포함(경량) | MVP | 상인 등록(AI 보조) | 모킹 |
| Product | 포함 | MVP | 검색/비교, 장보기(홈 직접 노출 제외) | 모킹 |
| DropEvent | 포함 | MVP | 드랍(입고 알림) | 모킹 |
| CatalogItem | 포함 | MVP | 홈 방문 유도 허브(드랍/행사/점포) | 모킹 |
| ShoppingList | 포함 | MVP | 장보기 리스트 | 모킹 |
| RoutePlan | 포함 | MVP | 지도/추천 동선 | 모킹(룰 기반) |
| Notification | 포함 | MVP | 알림함, 상태 안내 | 모킹 |

## 4. 엔터티별 상세 정의

## [Entity] User
- 설명: 인증/로그인의 주체가 되는 공통 사용자 계정 정보
- 주요 필드: `user_id`, `role`, `name`, `phone`, `home_market_id`, `created_at`
- 필수 필드
1. `user_id`
2. `role` (`consumer`/`merchant`)
3. `name`
- 옵션 필드
1. `phone`
- 데이터 출처: 모킹 데이터
- 비고: 상인 역할(`role=merchant`)의 User만 Merchant 프로필을 가질 수 있음

User - Market M:N 즐겨찾기, 알림설정

## [Entity] Market
- 설명: 전통시장 기본 정보
- 주요 필드: `market_id`, `market_name`, `address`, `lat`, `lng`, `region_code`, `zoom`
- 필수 필드
1. `market_id`
2. `market_name`
3. `address`
4. `lat`, `lng`
5. `zoom`
- 옵션 필드
1. `market_desc`
2. `open_hours`
- 데이터 출처: 공공데이터/API + 모킹 보정
- 비고: 좌표/주소는 공공데이터 우선, 설명 문구는 모킹

## [Entity] Store
- 설명: 시장 내 점포 정보 및 운영 기본 상태
- 주요 필드: `store_id`, `market_id`, `store_name`, `zone_label`, `lat`, `lng`, `phone`, `status`
- 필수 필드
1. `store_id`
2. `merchant_id`
3. `market_id`
4. `store_name`
5. `zone_label`
- 옵션 필드
1. `lat`, `lng`
2. `phone`
3. `store_story_summary`
4. `updated_at`
- 데이터 출처: 공공데이터/API + 모킹 보정
- 비고: MVP에서는 점포 상세 정보가 부족하면 `zone_label` 텍스트 안내로 대체

> 영업시간 필드 추가

## [Entity] Merchant
- 설명: 점포 운영을 위한 상인 프로필 정보
- 주요 필드: `merchant_id`, `user_id`, `display_name`, `description`, `active`
- 필수 필드
1. `merchant_id`
2. `user_id`
- 옵션 필드
1. `display_name`
2. `description`
3. `profile_image_url`
- 데이터 출처: 모킹 데이터
- 비고: 인증/권한은 User가 담당하고 Merchant는 운영 프로필만 담당

## [Entity] Product
- 설명: 점포별 판매 상품
- 주요 필드: `product_id`, `store_id`, `product_name`, `category`, `price`, `stock`, `image_url`, `quality_note`, `updated_at`
- 필수 필드
1. `product_id`
2. `store_id`
3. `product_name`
4. `price`
5. `stock` (int) 재고 테이블 구분하여 조회
- 옵션 필드
1. `category`
2. `image_url`
3. `updated_at`
- 데이터 출처: 모킹 데이터
- 비고: 가격은 ±10% 허용, 갱신 기준 24시간 1회

> 재고 테이블 별도 분리 (Inventory)
> -  drop event 연동
> - 유통기한 필드 추가
> - `quality_note` 품질

> 상인 스토리 테이블 추가 (Feed)

## [Entity] DropEvent
- 설명: 특정 상품 입고 이벤트
- 주요 필드: `drop_id`, `product_id`, `store_id`, `title`, `expected_at`, `status`, `subscriber_count`, `updated_at`
- 필수 필드
1. `drop_id`
2. `product_id`
3. `store_id`
4. `expected_at`
5. `status` (`예정`/`확정`/`지연`/`취소`)
- 옵션 필드
1. `title`
2. `subscriber_count`
3. `updated_at`
- 데이터 출처: 모킹 데이터
- 비고: MVP는 수동 등록, 이벤트 발생 시 즉시 반영

## [Entity] CatalogItem
- 설명: 홈 방문 유도 허브 노출 항목(드랍/행사/점포 스포트라이트)
- 주요 필드: `catalog_item_id`, `market_id`, `store_id`, `product_id`, `item_type`, `title`, `title_snapshot`, `image_snapshot`, `price_snapshot`, `badge`, `start_at`, `end_at`, `priority`
- 필수 필드
1. `catalog_item_id`
2. `market_id`
3. `item_type` (`drop`/`event`/`store_spotlight`)
4. `title`
5. `title_snapshot`
6. `image_snapshot`
- 옵션 필드
1. `store_id`
2. `product_id`
3. `price_snapshot`
4. `badge`
5. `start_at`, `end_at`
6. `priority`
- 데이터 출처: 모킹 데이터
- 비고: 홈 화면은 드랍 외 상품 상세 정보를 직접 노출하지 않고, 검색/상세 화면으로 이동시킴

## [Entity] ShoppingList
- 설명: 사용자 장보기 목록
- 주요 필드: `shopping_list_id`, `user_id`, `title`, `created_at`, `updated_at`
- 필수 필드
1. `shopping_list_id`
2. `user_id`
3. `title`
- 옵션 필드
1. `total_estimated_price`
2. `updated_at`
- 데이터 출처: 모킹 데이터
- 비고: MVP는 리스트 1~N개 허용, 공유 기능 제외

## [Entity] ShoppingListItem
- 설명: 장보기 목록의 개별 품목
- 주요 필드: `list_item_id`, `shopping_list_id`, `product_id`, `product_name_snapshot`, `qty`, `unit`, `checked`, `estimated_price`, `store_id`
- 필수 필드
1. `list_item_id`
2. `shopping_list_id`
3. `product_name_snapshot`
4. `qty`
5. `unit` (예: `개`/`g`/`kg`/`봉`/`팩`)
6. `checked`
- 옵션 필드
1. `product_id`
2. `estimated_price`
3. `store_id`
- 데이터 출처: 모킹 데이터
- 비고: UI 요구 기준 최소 필드(상품명/수량/체크 상태) 우선

## [Entity] RoutePlan
- 설명: 장보기 리스트 기반 추천 동선
- 주요 필드: `route_plan_id`, `user_id`, `market_id`, `shopping_list_id`, `route_json`, `estimated_minutes`, `created_at`
- 필수 필드
1. `route_plan_id`
2. `user_id`
3. `market_id`
4. `route_json`
- 옵션 필드
1. `shopping_list_id`
2. `estimated_minutes`
3. `distance_meters`
- 데이터 출처: 모킹 데이터
- 비고: MVP는 룰 기반 경로(최단거리 근사), 실내 정밀 네비 제외

## [Entity] Notification
- 설명: 드랍/운영/요청 관련 사용자 알림
- 주요 필드: `notification_id`, `user_id`, `type`, `title`, `body`, `target_screen_id`, `target_type`, `target_id`, `is_read`, `send_status`, `created_at`
- 필수 필드
1. `notification_id`
2. `user_id`
3. `type`
4. `title`
5. `target_type` (`product`/`drop`/`store`)
6. `is_read`
- 옵션 필드
1. `body`
2. `target_screen_id`
3. `target_id`
4. `send_status`
- 데이터 출처: 모킹 데이터
- 비고: `target_type + target_id` 조합으로 딥링크/라우팅 대상 명확화

## 5. 엔터티 간 관계 정의

1. `Market 1:N Store`
2. `Store 1:N Product`
3. `Store 1:N DropEvent`
4. `Store 1:N CatalogItem`
5. `User 1:0..1 Merchant` (상인 역할 User만 Merchant 프로필 보유)
6. `Store 1:1 Merchant` (MVP 기본) 또는 `Store 1:N Merchant` (실서비스 확장)
7. `User 1:N ShoppingList`
8. `ShoppingList 1:N ShoppingListItem`
9. `Product 1:N ShoppingListItem` (옵션 연결, 스냅샷 필드 우선)
10. `User 1:N RoutePlan`
11. `Market 1:N RoutePlan`
12. `User 1:N Notification`

## 6. MVP 모킹데이터 대체 영역

### 6.1 모킹데이터 필수 엔터티
- `Merchant`, `Product`, `CatalogItem`, `ShoppingList`, `ShoppingListItem`, `RoutePlan`, `Notification`

### 6.2 공공데이터로 대체가 어려운 이유
1. 시장 내부 점포-상인 매핑 데이터가 표준화되어 있지 않다.
2. 실시간 가격/재고/입고 이벤트는 공공데이터 제공 범위를 벗어난다.
3. 상인 스토리/운영 맥락 데이터는 현장 입력 기반 데이터다.

### 6.3 시연 구현 수준
1. `Market`, `Store`는 일부 공공데이터 + 정제된 모킹으로 안정화한다.
2. `Product`, `CatalogItem`은 시나리오 기반 고정 데이터셋으로 운영한다.
3. `RoutePlan`은 좌표 + 룰 기반 JSON으로 생성한다.
4. `Notification`은 인앱 중심으로만 구현해 시연 안정성을 높인다.
5. 홈은 `CatalogItem(item_type=drop/event/store_spotlight)` 중심으로 구성하고 일반 상품 카드는 검색 화면으로 분리한다.

## 7. 구현 우선순위

### P0 (즉시 구현)
- `Market`
- `Store`
- `Product`
- `CatalogItem`
- `User`
- `Merchant`
- `ShoppingList`
- `ShoppingListItem`
- `Notification`

### P1 (MVP 고도화)
- `RoutePlan`

## 8. MVP 통합 모델 제안 (Store-Merchant)

1. 기본안
- `Store`와 `Merchant` 분리 유지
- 장점: Phase 2 확장 시 변경 비용이 낮다.

2. 단순안
- `Merchant`를 `Store` 내부 속성(`owner_name`, `owner_phone`)으로 통합
- 장점: 테이블 수 감소, 빠른 구현
- 단점: 상인 계정 기능 확장 시 마이그레이션 필요

3. 권장안
- DB는 분리(`Store`, `Merchant`)하되 API 응답은 통합 DTO로 제공
- MVP 구현 속도와 확장성을 동시에 확보

## 9. 개발 메모 (실행 가이드)

1. 검색/비교 API는 `Product` + `Store` 조인만으로 우선 구현한다.
2. 카탈로그(홈 허브)는 `CatalogItem` 우선이며 `drop/event/store_spotlight` 타입만 홈에 노출한다.
3. 장보기 리스트는 `ShoppingListItem.product_name_snapshot`를 기본 표시값으로 사용한다.
4. 지도/동선은 `Store.zone_label` 텍스트 안내를 항상 함께 반환한다.

## 10. AI 시연 구현 필수 연동 항목

### 10.1 필수 외부 연동 (시연 기준)
1. LLM API (텍스트 생성/요약/추천)
- 대상 기능: 장보기 에이전트(RAG), 상인 스토리 생성, 가격/재고 제안 문구 생성
2. 임베딩/검색(RAG) 구성
- 대상 기능: 레시피/장보기 추천의 근거 검색
3. 이미지/음성 인식 API (또는 동등 모듈)
- 대상 기능: 상인 상품 등록 AI 보조(이미지/음성 → 상품정보 구조화)

### 10.2 시연 성공 기준 (AI 기능)
1. 장보기 에이전트: 사용자 질의 입력 시 메뉴/재료/매칭 결과를 실제 생성
2. AI 상품 등록: 이미지/음성 입력 시 상품명/카테고리/설명 자동 채움
3. AI 운영 보조: 가격/재고 제안 결과와 사유 문구 출력

### 10.3 미연동 시 대체 규칙 (Fallback)
1. LLM 실패 시: 사전 준비된 템플릿 응답 + 재시도 안내 노출
2. 인식 API 실패 시: 수동 입력 폼 자동 전환
3. RAG 검색 실패 시: 기본 레시피 데이터셋 기반 추천으로 대체

### 10.4 팀원 작업 요청 (추가)
1. API 키/환경변수 분리 관리 (`.env`/시크릿)
2. 데모 계정 기준 호출량 제한 설정(비용 보호)
3. 실패 로그 수집(요청 시각, 기능, 에러 코드)으로 시연 리스크 대응
