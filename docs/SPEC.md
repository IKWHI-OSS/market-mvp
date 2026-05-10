
# 전통시장 소비자-상인 연결 서비스 — Market Info

## Specify(명세 단계)

#### 사용자 혹은 이해관계자가 어떤 문제를 갖고 있고, 어떤 조건이 충족되면 해결될 것인가를 서술한다. 데이터의 출처, 신뢰도, 갱신 주기, 접근 권한을 명세에 추가한다.

**function**: 전통시장 상품 정보의 디지털 제공 및 AI 기반 운영 보조를 통해 소비자의 장보기 행동을 전통시장 방문으로 전환하는 모바일 서비스

**Purpose**: 소비자는 방문 전 신뢰할 수 있는 상품 정보를 확인하고 드랍(입고) 알림을 받아 시장 방문을 결정한다. 상인은 AI 보조로 입력 부담 없이 상품을 노출하고 가격·재고 운영 효율을 개선한다.

**usercase**: {
  소비자: 홈 허브에서 드랍/행사/점포 스포트라이트 확인 → 드랍 구독 → 상품 검색/비교 → 시장 방문,
  상인: 상품 사진·텍스트 입력 → AI 자동 구조화 → 검토 후 게시 → 재고·가격 운영 보조 수신
}

**service_target**: {
  시장: 망원시장 (서울 마포구, 시연 기준)
  점포: 10개 (야채 2, 과일 2, 수산 2, 정육 1, 반찬 1, 잡화 1, 건어물 1)
  상품: 48개 (점포당 4~5개, 실 시세 ±10% 기준 모킹)
  유저: 5명 (consumer 2, merchant 2, operator 1)
  드랍: 12개 (arrived 4, scheduled 6, sold_out 2)
}

**backend_current_state**: {
  Phase 1: FastAPI + SQLAlchemy + MySQL 8.0, 72 tests 통과, Railway 배포 중,
  Phase 2: 코드 완성 (36 tests), Railway 미배포,
  Phase 2 신규 테이블: MarketPrice·ProductPriceHistory 미생성 (schema.sql에만 존재),
  배포 URL: https://market-api-production-6e52.up.railway.app
}

**ERD**: User(1)----(N)Merchant(N)----(1)Store(N)----(N)Product
         Market(1)----(N)Store(N)----(N)DropEvent
         User(1)----(N)ShoppingList(1)----(N)ShoppingListItem
         User(1)----(N)RoutePlan, User(1)----(N)Notification
         [Phase 2 추가] Product(1)----(N)ProductPriceHistory, MarketPrice(독립)
         [고도화 대상] Product(1)----(1)Inventory, Store(1)----(N)Story

**data_source**: {
  모킹 데이터: Merchant·Product·CatalogItem·ShoppingList·DropEvent·Notification (시연 안정성 우선),
  공공데이터: Market·Store 기본 정보 (서울 열린데이터광장),
  외부 API: KAMIS 농산물 시세 (API 키 필요, fallback 구현됨),
  LLM: Anthropic Claude Haiku (스토리 생성·AI draft·장보기 에이전트, ANTHROPIC_API_KEY 필요)
}

**range**: 백엔드 API 서버 고도화가 현재 범위이며, Flutter 프론트엔드는 백엔드 완성 후 착수한다.
          외부 API 키가 필요한 기능(KAMIS 실시간, FCM 푸시)은 fallback 구조를 갖추고 후순위로 배치한다.
          결제·정산·소셜로그인·음성인식·실내 정밀 지도는 현재 범위 밖이다.
          운영자(operator) 역할은 CatalogItem 관리 범위로만 제한 활성화한다.

**non_functional_req**: 모킹 데이터 의존도가 높아 실데이터 전환 시 구조 변경이 발생할 수 있다.
                        KAMIS API 품목 코드가 7개로 하드코딩되어 있어 확장 시 수동 추가가 필요하다.
                        Preorder 구독자 목록이 없어 드랍 arrived 전환 시 알림 대상 특정이 불완전하다.
                        Product.stock_status와 Inventory 테이블 분리 시 기존 API 응답 구조 변경이 발생한다.

**constraints**: Railway MySQL 무료 플랜의 커넥션 수·스토리지 용량 제한이 있다.
                ANTHROPIC_API_KEY 미설정 시 story_service·agent_service가 fallback 모드로 동작한다.
                FCM 푸시 알림은 앱 배포 없이 테스트 불가하여 인앱 알림으로만 구현한다.
                Flutter 프론트엔드는 백엔드 API 계약서 확정 이후 착수하며 백엔드 breaking change를 허용하지 않는다.

**completion_standard**: 백엔드가 다음 조건을 충족하면 프론트엔드 착수를 선언한다.
                         1차: 전체 130+ tests 통과, Railway 배포 안정,
                         2차: 소비자·상인 핵심 플로우 E2E curl 테스트 통과,
                         3차: /docs OpenAPI 문서가 프론트 연동 계약서로 사용 가능한 상태,
                         4차: 외부 API 없이도 fallback으로 전 기능 동작 확인.



## Plan(ADR 계획 단계)

### Specify를 Architecture Decision Records로 전환하는 단계로, 왜 다른 선택지를 배제했고, 왜 이런 선택을 했는지를 문서화 한다.

### 불확실성이 높은 결정에 대해서 명시적으로 **이 결정은 [조건]이 확인된 후 재검토**

---

## ADR-00: 개발 전략 — 백엔드 선행 순차 개발

**Status**: 채택

**맥락**
백엔드 Phase 1은 배포 완료, Phase 2는 코드 완성 미배포 상태다.
Flutter 프론트엔드는 계획만 존재하고 구현이 없다.
두 영역을 동시에 개발할 경우 API 계약 충돌과 컨텍스트 스위칭 비용이 발생한다.

**결정**
백엔드를 완성 기준까지 먼저 고도화한 뒤 OpenAPI 계약서를 확정하고 프론트엔드를 착수한다.

**이유**
백엔드가 API 계약서 역할을 하면 프론트엔드는 해당 계약서만 보고 독립적으로 개발할 수 있다.
백엔드 개발자 관점에서 컨텍스트 스위칭 없이 집중도가 높아진다.
프론트엔드 착수 이후 백엔드 breaking change를 금지함으로써 연동 충돌을 원천 차단한다.

**영향**
백엔드 완료 선언 이후 API 경로·응답 필드 삭제·타입 변경은 v2 에서만 허용한다.
optional 필드 추가는 언제든 허용한다.

---

## ADR-01: 기술 스택 확정

**Status**: 채택

**맥락**
Phase 1 구현이 완료된 상태로 기술 스택 변경 비용이 크다.

**결정**
백엔드: FastAPI + SQLAlchemy + MySQL 8.0 (Railway), 프론트엔드: Flutter (Dart)

**이유**
FastAPI는 OpenAPI 문서 자동 생성으로 계약서 역할을 즉시 수행한다.
SQLAlchemy ORM이 MySQL과 SQLite(테스트) 모두 지원하여 CI 환경 분리가 용이하다.
Railway는 MySQL + 자동 배포를 무료 플랜에서 지원한다.

**영향**
테스트 환경은 SQLite(`sqlite:////tmp/test.db`)를 사용하여 Railway DB 의존 없이 로컬 실행 가능하다.

---

## ADR-02: DB 소프트 딜리트 전면 적용

**Status**: 채택

**맥락**
현재 DELETE 엔드포인트는 물리 삭제를 수행한다.
삭제된 데이터의 복구 불가, 알림·이력 참조 단절 문제가 발생한다.

**결정**
Product·DropEvent·ShoppingList·ShoppingListItem·Notification·Preorder·Story 테이블에
`deleted_at DATETIME DEFAULT NULL` 컬럼을 추가하고 소프트 딜리트로 전환한다.

**이유**
드랍 취소·상품 삭제 시 연결된 Notification·Preorder 레코드의 참조 무결성을 유지한다.
삭제 이력 보존으로 향후 분석·복구가 가능하다.

**영향**
모든 조회 쿼리에 `deleted_at IS NULL` 필터 추가가 필요하다.
적용 후 기존 테스트 전체 재실행으로 회귀 여부 확인이 필수이다.
이 결정은 T-03 완료 후 기존 테스트 회귀 결과를 확인한 뒤 재검토한다.

---

## ADR-03: Inventory 테이블 분리

**Status**: 채택

**맥락**
현재 Product 테이블에 `stock_status` 재고 필드가 혼재한다.
재고는 가격·상품명보다 갱신 빈도가 높아 Product 전체 조회 시 불필요한 I/O가 발생한다.

**결정**
재고 관련 필드를 독립 Inventory 테이블로 분리한다.
API 응답은 Product + Inventory JOIN으로 통합 DTO를 제공하여 기존 응답 구조를 유지한다.

**이유**
ERD 메모에 "재고 테이블 별도 분리" 요구사항이 명시되어 있다.
유통기한 필드 추가, 드랍 이벤트 연동이 Inventory 분리 이후 자연스럽게 확장된다.
재고 상태만 변경하는 빈번한 PATCH 요청이 Product 전체 레코드 락을 회피한다.

**영향**
Product 응답 스키마에 `inventory` 중첩 객체가 추가된다.
기존 `stock_status` 직접 참조 코드를 JOIN 방식으로 전환해야 한다.
이 결정은 프론트엔드 착수 전에 완료되어야 하며 이후 구조 변경은 금지한다.

---

## ADR-04: Feed/Story 저장 구조

**Status**: 채택

**맥락**
Phase 2의 `story_service.py`는 LLM으로 스토리를 생성하지만 DB에 저장하지 않는다.
생성 결과가 유실되어 상인이 재생성을 반복해야 하고 게시 이력 관리가 불가하다.

**결정**
Story 테이블을 신규 생성하고 생성 결과를 저장·게시·수정·조회 가능한 구조로 전환한다.
소비자는 게시된 스토리만 조회 가능하고 상인은 본인 점포 스토리 전체를 관리한다.

**이유**
ERD 메모에 "상인 스토리 테이블 추가(Feed)" 요구사항이 명시되어 있다.
게시 전 편집·승인 단계는 Functional Specification FR-M-04의 수용 기준이다.
LLM 비용 절감 효과도 있다 (재생성 없이 저장된 결과 재활용).

**영향**
`POST /merchant/stories` 응답에 `story_id`가 추가된다.
게시 토글 API가 신규 추가된다.
`GET /stores/{store_id}/story` 소비자용 엔드포인트가 신규 추가된다.

---

## ADR-05: 장보기 에이전트 구현 방식

**Status**: 채택

**맥락**
Functional Specification FR-C-03 장보기 에이전트는 Phase 3으로 분류되어 있다.
RAG 구성(임베딩 DB, 벡터 검색)은 별도 인프라가 필요하여 현재 범위를 초과한다.
단, 자연어 입력 → 재료 추출 → 상품 매칭의 기본 흐름은 LLM 하나로 구현 가능하다.

**결정**
임베딩 DB 없이 Anthropic Haiku 단일 호출로 재료를 추출하고 Product DB에서 FULLTEXT 매칭하는
경량 에이전트를 구현한다. LLM 미사용 시 키워드 사전 기반 fallback으로 동작한다.

**이유**
기존 ANTHROPIC_API_KEY가 Phase 2에서 이미 사용 중이므로 추가 인프라 없이 구현 가능하다.
fallback 구현으로 외부 API 없이도 기본 기능이 동작한다.
RAG 고도화는 Phase 3으로 명확히 분리하여 현재 범위 초과를 방지한다.

**영향**
`POST /agent/shopping` 신규 엔드포인트 추가.
`fallback_mode` 필드로 LLM 사용 여부를 응답에 명시한다.
이 결정은 ANTHROPIC_API_KEY가 환경변수에 설정된 조건에서만 LLM 경로가 활성화된다.

---

## ADR-06: 상인 드랍 직접 관리 API 추가

**Status**: 채택

**맥락**
현재 DropEvent는 모킹 데이터로만 존재하며 상인이 직접 드랍을 등록·수정·상태 변경할 API가 없다.
Functional Specification FR-M-03에 "예정입고 관리(입고일시, 수량 등록)" 요구사항이 명시되어 있다.

**결정**
상인 전용 드랍 관리 API를 추가한다.
상태 전이: `scheduled → arrived → sold_out`, 단방향, 역방향 불가.
상태 변경 시 Notification을 자동 생성한다.

**이유**
모킹 데이터에만 의존하면 시연 시나리오에서 상인 행동이 시연 불가하다.
드랍 arrived 전환이 소비자 알림 트리거이므로 상인 수동 전환 API가 필수이다.

**영향**
`POST /merchant/drops` 등 5개 엔드포인트 신규 추가.
DropEvent 삭제는 소프트 딜리트로 처리한다.
Preorder 연동: arrived 전환 시 pending 상태 Preorder 소유자에게 자동 알림.

---

## ADR-07: 점포·시장 독립 조회 API 추가

**Status**: 채택

**맥락**
현재 Store·Market 데이터는 홈·검색 응답에 포함되어 반환되지만 독립적인 상세 조회 API가 없다.
프론트엔드 점포 상세 화면(SCR-C-03 연관), 시장 탐색 화면에서 별도 호출이 필요하다.

**결정**
`GET /markets`, `GET /markets/{id}`, `GET /stores/{id}`,
`GET /stores/{id}/products`, `GET /stores/{id}/drops`, `GET /stores/{id}/story` 를 추가한다.

**이유**
프론트엔드 화면 단위와 API 단위를 1:1로 매핑하여 연동 복잡도를 낮춘다.
점포 상세에서 영업시간·구역·스토리를 하나의 API로 제공하면 요청 수가 감소한다.

**영향**
Store 응답 DTO에 `story` 중첩 객체(게시된 것만)가 추가된다.
Market 응답 DTO에 `store_count` 필드가 추가된다.

---

## ADR-08: 외부 API 의존성 처리 원칙

**Status**: 채택

**맥락**
KAMIS 농산물 시세 API, ANTHROPIC_API_KEY, FCM 등 외부 의존성이 여러 곳에 있다.
API 키 미설정 시 서버가 실패하거나 기능 전체가 비활성화되는 것은 시연 위험 요소다.

**결정**
모든 외부 API는 `fallback_mode=true` 로 동작하는 대체 경로를 반드시 구현한다.
환경변수 미설정 시 서버 기동 실패가 아닌 해당 기능 fallback 전환으로 처리한다.

**이유**
Phase 2에서 이미 `story_service.py`에 fallback 패턴이 구현되어 있어 일관된 확장이 가능하다.
시연 중 외부 API 장애가 발생해도 핵심 플로우가 중단되지 않는다.

**영향**
모든 외부 API 서비스에 `try/except` + fallback 응답 구조가 표준으로 적용된다.
`fallback_mode` 필드가 해당 응답에 포함되어 프론트엔드가 UX를 분기할 수 있다.

---

## ADR-09: 응답 캐싱 전략

**Status**: 채택

**맥락**
홈 피드·드랍 리스트는 모킹 데이터 기반으로 매 요청마다 DB를 조회할 필요가 없다.
시연 환경에서 불필요한 DB 부하를 줄여 응답 안정성을 높인다.

**결정**
인메모리 캐시(`cachetools.TTLCache`)를 사용한다. Railway Redis 플러그인은 비용 발생으로 후순위.
TTL: `/home` 5분, `/drops` 2분, `/markets` 30분, `/catalog` 10분

**이유**
Railway 무료 플랜에서 Redis 플러그인 추가 없이 즉시 적용 가능하다.
캐시 키를 `market_id + query_params` 조합으로 설정하면 데이터 정합성이 유지된다.

**영향**
드랍 상태 변경 시 관련 캐시를 수동으로 무효화하는 로직이 필요하다.
단일 프로세스 환경(Railway 단일 컨테이너)에서만 유효하며 멀티 인스턴스 확장 시 재검토한다.

---

## ADR-10: Rate Limiting 적용 기준

**Status**: 채택

**맥락**
LLM API 호출(스토리 생성, AI draft, 장보기 에이전트)은 호출당 비용이 발생한다.
제한 없이 열어두면 시연 환경에서 예상치 못한 비용이 발생한다.

**결정**
`slowapi` 라이브러리로 엔드포인트별 Rate Limit을 적용한다.
기준: `POST /auth/login` 10 req/min per IP,
      `POST /agent/shopping` 20 req/min per user,
      `POST /merchant/stories` 5 req/min per user,
      `POST /merchant/products/ai-draft` 10 req/min per user

**이유**
`slowapi`는 FastAPI와 구조적으로 호환되며 데코레이터 방식으로 비침습적 적용이 가능하다.

**영향**
429 응답이 공통 에러 포맷(`code: RATE_LIMITED`)으로 통일되어야 한다.

---

## ADR-11: Operator API 활성화 범위

**Status**: 채택

**맥락**
DB에 `User.role = 'operator'` ENUM이 존재하지만 API가 전면 비활성 상태다.
CatalogItem(홈 피드)은 현재 모킹 데이터로만 관리되어 운영 중 피드 수정이 불가하다.

**결정**
Operator API는 CatalogItem CRUD 범위로만 제한하여 최소 활성화한다.

**이유**
시연 중 홈 피드 콘텐츠를 실시간으로 수정할 수 있어야 시나리오 대응이 가능하다.
전체 운영 대시보드(FR-A-03)는 MVP에서 제외로 확정되어 있으므로 범위 초과를 방지한다.

**영향**
`GET/POST/PATCH/DELETE /operator/catalog` 4개 엔드포인트 신규 추가.
`role=operator` 검증 미들웨어가 신규 적용된다.



## Tasks(작업 단계)

### '단일 책임'을 가져야 하고, 독립적으로 검증 가능해야 한다. 원천 데이터의 스키마를 검증하고 함수를 작성 및 테스트 하는 것처럼 **완료 여부**를 판단할 수 있는 단위로만 작성, 가설은 배경이고, Tasks가 가설을 검증하는 행동으로 작용.

### 의존성이 불명확하면 진행 중 충돌이 발생할 수 있으므로, 반드시 **선행조건** 을 포함.

---

## T-00: Phase 2 Railway 배포

**Status**: 진행 전

**What**: Phase 2 코드(가격·스토리·Preorder)를 Railway에 배포하고 전체 108 tests 통과를 확인한다.

**선행조건**: 없음

**완료조건**:
- □ Phase 2 로컬 테스트 36 passed: `pytest tests/test_prices.py tests/test_stories.py tests/test_preorders.py -v`
- □ Railway MySQL에 MarketPrice·ProductPriceHistory 테이블 생성 완료
- □ ANTHROPIC_API_KEY Railway 환경변수 설정 확인
- □ git push → Railway 자동 배포 성공
- □ 스모크 테스트 통과: `GET /health`, `GET /api/v1/home`, `GET /api/v1/drops`

**결과**: (작업 후 기입)

---

## T-01: Inventory 테이블 분리

**Status**: 진행 전

**What**: Product의 재고 필드를 독립 Inventory 테이블로 분리하고 재고 관리 API를 구현한다.

**선행조건**: T-00 완료 (Railway 배포 안정 확인 후 스키마 변경)

**완료조건**:
- □ db/schema.sql에 Inventory 테이블 DDL 추가 (inventory_id, product_id UNIQUE FK, stock_status ENUM, quantity, expiry_date, deleted_at)
- □ SQLAlchemy Inventory 모델 생성 (app/db/models/inventory.py)
- □ InventoryRepository CRUD (get_by_product_id, get_risk_inventory, update_status, bulk_create)
- □ ProductService에서 Product + Inventory JOIN으로 통합 응답 제공
- □ 신규 API 3개 동작 확인: `GET /merchant/inventory`, `GET /merchant/inventory/risk`, `PATCH /merchant/inventory/{product_id}`
- □ mock/inventory.json 생성 및 seed_mock.py에 Inventory 시드 추가
- □ test_inventory.py 10 tests 이상 통과
- □ 기존 Product 관련 테스트 회귀 없음

**결과**: (작업 후 기입)

---

## T-02: Feed/Story 테이블 추가 및 API 확장

**Status**: 진행 전

**What**: 상인 스토리 저장·조회·게시 구조를 구현하고 기존 story_service를 저장 연동으로 전환한다.

**선행조건**: T-00 완료

**완료조건**:
- □ db/schema.sql에 Story 테이블 DDL 추가 (story_id, store_id FK, merchant_id FK, title, content, tone, length_type ENUM, is_published, deleted_at)
- □ SQLAlchemy Story 모델 생성 (app/db/models/story.py)
- □ StoryRepository CRUD (create, get_by_id, get_by_store, get_by_merchant, update, soft_delete, toggle_publish)
- □ story_service.py 수정: LLM 생성 결과를 Story 테이블에 저장, 응답에 story_id 포함
- □ 신규 API 동작 확인: `GET /merchant/stories`, `GET /merchant/stories/{id}`, `PATCH /merchant/stories/{id}`, `PATCH /merchant/stories/{id}/publish`, `GET /stores/{store_id}/story`
- □ test_stories.py 15 tests 이상 통과 (기존 9 + 신규 6)

**결과**: (작업 후 기입)

---

## T-03: 소프트 딜리트 전면 적용

**Status**: 진행 전

**What**: 물리 삭제 방식을 deleted_at 기반 소프트 딜리트로 전환한다.

**선행조건**: T-01, T-02 완료 (신규 테이블에 deleted_at이 이미 포함된 상태로 설계)

**완료조건**:
- □ db/soft_delete_migration.sql 생성: Product·DropEvent·ShoppingList·ShoppingListItem·Notification·Preorder 테이블에 `ALTER TABLE ADD COLUMN deleted_at DATETIME DEFAULT NULL`
- □ Railway DB에 마이그레이션 적용 완료
- □ SQLAlchemy BaseMixin에 `deleted_at` 컬럼 및 `soft_delete()` 메서드 추가
- □ 각 Repository의 get_all, get_by_id 쿼리에 `deleted_at IS NULL` 필터 적용
- □ 기존 DELETE 엔드포인트 소프트 딜리트 전환 (`DELETE /shopping-lists/{id}/items/{item_id}` 등)
- □ 기존 전체 테스트 회귀 없음: `pytest tests/ -v` 모두 통과

**결과**: (작업 후 기입)

---

## T-04: FULLTEXT INDEX 적용 및 검색 개선

**Status**: 진행 전

**What**: MySQL ngram 파서 기반 FULLTEXT INDEX를 적용하여 한글 상품명 검색 정확도를 향상한다.

**선행조건**: T-00 완료 (Railway DB 접근 가능 상태)

**완료조건**:
- □ Railway MySQL에 FULLTEXT INDEX 적용: `ALTER TABLE Product ADD FULLTEXT INDEX ft_product_name (product_name, category) WITH PARSER ngram`
- □ Store 테이블에도 동일 적용: `ft_store_name (store_name) WITH PARSER ngram`
- □ ProductRepository search 메서드: FULLTEXT MATCH AGAINST 우선 → 결과 없으면 LIKE fallback
- □ 검색 테스트 통과: '딸기', '수산', '단감', '야채' 키워드 각각 1개 이상 결과 반환

**결과**: (작업 후 기입)

---

## T-05: PriceHistory 자동 기록 연동

**Status**: 진행 전

**What**: 상품 가격 변경 시 ProductPriceHistory 테이블에 자동으로 이력이 기록되도록 연동한다.

**선행조건**: T-00 완료 (ProductPriceHistory 테이블 Railway에 생성된 상태)

**완료조건**:
- □ ProductService의 가격 업데이트 로직 실행 시 PriceHistory 레코드 자동 생성
- □ `GET /merchant/products/{id}/price-history` 응답에 최근 30일 이력 + change_rate + change_amount 필드 포함
- □ test_prices.py 이력 자동 기록 테스트 추가

**결과**: (작업 후 기입)

---

## T-06: 점포·시장 상세 API 구현

**Status**: 진행 전

**What**: 점포·시장 독립 조회 API를 구현하여 프론트엔드 화면별 데이터 요청을 지원한다.

**선행조건**: T-02 완료 (Story 테이블 및 API 존재, 점포 상세에서 스토리 포함 반환)

**완료조건**:
- □ MarketRepository get_all, get_by_id(with store_count) 구현
- □ StoreRepository get_by_id_detail (Merchant + 게시 Story 포함), get_products_by_store, get_drops_by_store 구현
- □ app/api/v1/markets.py 생성: `GET /markets`, `GET /markets/{market_id}`
- □ app/api/v1/stores.py 생성: `GET /stores/{store_id}`, `GET /stores/{store_id}/products`, `GET /stores/{store_id}/drops`, `GET /stores/{store_id}/story`
- □ router.py에 markets, stores 라우터 등록
- □ test_markets.py, test_stores.py 각 8 tests 이상 통과

**결과**: (작업 후 기입)

---

## T-07: 상인 드랍 관리 API 구현

**Status**: 진행 전

**What**: 상인이 드랍 이벤트를 직접 등록·수정·상태 변경·취소할 수 있는 API를 구현한다.

**선행조건**: T-03 완료 (DropEvent 소프트 딜리트 적용 후), T-00 완료

**완료조건**:
- □ app/services/merchant_drop_service.py 생성 (create_drop, update_drop, change_status, cancel_drop)
- □ 상태 전이 유효성: scheduled→arrived·sold_out, arrived→sold_out 만 허용. 역방향 409 반환
- □ arrived 전환 시 Notification 자동 생성 (type=drop_arrived, target_type=drop)
- □ 신규 API 5개 동작 확인: `POST /merchant/drops`, `GET /merchant/drops`, `PATCH /merchant/drops/{id}`, `PATCH /merchant/drops/{id}/status`, `DELETE /merchant/drops/{id}`
- □ test_merchant_drops.py 12 tests 이상 통과
  - □ 드랍 등록, 수정, 상태 변경, 취소 정상 흐름
  - □ 타인 드랍 수정 시 403
  - □ 잘못된 상태 전이 시 409
  - □ arrived 전환 시 Notification 레코드 생성 확인

**결과**: (작업 후 기입)

---

## T-08: 상품 수정·삭제 API 구현

**Status**: 진행 전

**What**: 상인이 등록된 상품을 수정하고 소프트 딜리트할 수 있는 API를 구현한다.

**선행조건**: T-03 완료 (Product 소프트 딜리트 적용)

**완료조건**:
- □ ProductRepository에 update, soft_delete 메서드 추가
- □ 신규 API 3개 동작 확인: `PATCH /merchant/products/{id}`, `DELETE /merchant/products/{id}`, `PATCH /merchant/products/{id}/status`
- □ 권한 검증: 본인 점포 상품만 수정·삭제 가능, 타인 시도 시 403
- □ 삭제 후 `GET /merchant/inventory`에서 해당 상품 비노출 확인

**결과**: (작업 후 기입)

---

## T-09: 장보기 에이전트 기본 구현

**Status**: 진행 전

**What**: 자연어 입력을 재료 목록으로 변환하고 Product DB에서 매칭하여 장보기 제안을 반환한다.

**선행조건**: T-04 완료 (FULLTEXT 검색으로 재료 매칭 정확도 확보)

**완료조건**:
- □ app/services/agent_service.py 생성
  - □ `extract_ingredients_llm()`: Anthropic Haiku 호출, 재료 JSON 배열 반환
  - □ `extract_ingredients_keyword()`: 식재료 사전(100개 품목) 기반 키워드 추출 fallback
  - □ `match_products_to_ingredients()`: FULLTEXT 검색으로 재료별 Product 매칭
- □ app/schemas/agent.py 생성 (ShoppingAgentRequest, ShoppingAgentResponse)
- □ app/api/v1/agent.py 생성: `POST /agent/shopping`, `POST /agent/shopping/save`
- □ router.py에 agent 라우터 등록
- □ test_agent.py 10 tests 이상 통과 (LLM mock 포함)
  - □ 기본 쿼리 응답 정상
  - □ ANTHROPIC_API_KEY 미설정 시 fallback_mode=true 반환
  - □ /save 호출 시 ShoppingList 레코드 생성 확인

**결과**: (작업 후 기입)

---

## T-10: 동선 알고리즘 개선

**Status**: 진행 전

**What**: ShoppingListItem 기반 동선을 zone_label 그룹화 및 인접 구역 순서 정렬로 개선한다.

**선행조건**: T-00 완료

**완료조건**:
- □ route_service.py 알고리즘 개선: store_id → zone_label 그룹화 → 인접 구역 순서 정렬
- □ route_json 응답 구조 변경: `{ route: [{ step, zone, stores[], estimated_minutes }], total_estimated_minutes, total_stores }`
- □ `zone_label` 텍스트 안내가 모든 route 응답에 포함됨 확인
- □ test_routes.py 업데이트: 신규 응답 구조 기준으로 테스트 재작성

**결과**: (작업 후 기입)

---

## T-11: Operator CatalogItem API 구현

**Status**: 진행 전

**What**: 운영자(role=operator) 전용 CatalogItem CRUD API를 구현하여 홈 피드를 관리한다.

**선행조건**: T-00 완료

**완료조건**:
- □ app/api/v1/operator.py 생성: `GET /operator/catalog`, `POST /operator/catalog`, `PATCH /operator/catalog/{id}`, `DELETE /operator/catalog/{id}`
- □ role=operator 권한 검증 미들웨어 적용 (consumer·merchant 시도 시 403)
- □ CatalogItem 소프트 딜리트 연동 (T-03 선행)
- □ test_operator.py 8 tests 이상 통과

**결과**: (작업 후 기입)

---

## T-12: 응답 캐싱 적용

**Status**: 진행 전

**What**: 홈 피드·드랍 리스트·시장 목록에 TTL 기반 인메모리 캐시를 적용한다.

**선행조건**: T-06, T-07 완료 (캐시 무효화 대상 API 존재 확인 후 적용)

**완료조건**:
- □ `cachetools` 설치 및 TTLCache 캐시 레이어 구성
- □ 캐시 적용 엔드포인트: `/home` (5분), `/drops` (2분), `/markets` (30분), `/catalog` (10분)
- □ 캐시 키: `{endpoint}:{market_id}:{query_params}` 조합
- □ 드랍 상태 변경(T-07) 시 `/home`, `/drops` 관련 캐시 무효화 확인

**결과**: (작업 후 기입)

---

## T-13: Rate Limiting 적용

**Status**: 진행 전

**What**: LLM 비용 보호 및 로그인 브루트포스 방지를 위한 Rate Limit을 적용한다.

**선행조건**: T-09 완료 (agent API 존재 확인 후 일괄 적용)

**완료조건**:
- □ `slowapi` 설치 및 FastAPI 미들웨어 등록
- □ 엔드포인트별 리밋 적용: 로그인 10/min, 에이전트 20/min, 스토리 5/min, AI draft 10/min
- □ 429 응답이 공통 에러 포맷 `{ success: false, code: "RATE_LIMITED" }` 로 반환됨 확인

**결과**: (작업 후 기입)

---

## T-14: Health Check 강화

**Status**: 진행 전

**What**: DB·외부 API 상태를 포함한 상세 헬스 체크 엔드포인트를 추가한다.

**선행조건**: 없음

**완료조건**:
- □ `GET /health/detail` 구현: DB 연결 latency, ANTHROPIC_API_KEY 존재 여부, KAMIS_API_KEY 존재 여부, 캐시 상태 포함
- □ 각 항목 status: `ok` / `degraded` / `error` 3단계 반환
- □ 전체 status는 하위 항목 중 가장 낮은 등급으로 집계

**결과**: (작업 후 기입)

---

## T-15: 테스트 전체 보강

**Status**: 진행 전

**What**: T-01~T-14 신규 기능 테스트와 E2E 시나리오 테스트를 추가하여 전체 130+ tests를 달성한다.

**선행조건**: T-01~T-14 전체 완료

**완료조건**:
- □ 전체 `pytest tests/ -v` 130 tests 이상 통과
- □ E2E 소비자 시나리오 테스트: 로그인 → 홈 조회 → 드랍 구독 → 상품 검색 → 알림 확인
- □ E2E 상인 시나리오 테스트: 로그인 → 드랍 등록 → AI draft → 상품 게시 → 재고 업데이트
- □ Edge case: 빈 데이터, 잘못된 입력, 권한 없음, fallback_mode 동작 각 1개 이상

**결과**: (작업 후 기입)

---

## T-16: OpenAPI 문서 완성 및 프론트 계약서 배포

**Status**: 진행 전

**What**: 모든 엔드포인트에 문서를 작성하고 프론트엔드 연동 계약서로 확정한다.

**선행조건**: T-15 완료 (모든 기능 안정 확인 후 문서 고정)

**완료조건**:
- □ 모든 엔드포인트에 summary, description, response_model 기재
- □ 인증 필요 여부(🔒) 명시
- □ Railway 배포 URL의 `/docs` 접근 및 Try it out 정상 동작 확인
- □ API_Specification.md 최신화 (신규 엔드포인트 전체 반영)
- □ 프론트엔드 연동용 테스트 계정·시드 데이터 정보 문서화
- □ **백엔드 완료 선언** — 이후 breaking change 금지

**결과**: (작업 후 기입)



## Implement(구현 단계)

### 코드는 명세의 표현이므로 구현 중 명세와 다른 결정을 해야 하는 상황이 생기면 코드를 명세에 맞추는 것이 아닌, 명세를 수정하고 코드를 생성하는 규율을 지켜야 한다. 이 규율이 무너지면 명세와 코드의 중요도가 전복된다.

### 데이터 결측, 형식 불일치, 이상값 등 발생했을 때 Specify로 돌아가야 하는 신호로서, 버그로 처리하지 말고 명세 갱신 트리거로 다뤄야 한다.

### 코드를 작성하면서 채워지는 섹션으로 코드 파일 링크, Plan에서 벗어난 결정과 그 이유, 구현 도중 발생한 명세 수정 이력이 기록된다.

### 에이전트 실행 규칙
- 모든 작업은 브랜치 단위로 진행한다: `feature/tier1-db`, `feature/tier2-api`, `feature/tier3-ops`
- 파일 생성 후 반드시 해당 Task의 완료조건을 체크하고 보고한다
- SPEC.md는 읽기만 허용하며 수정하지 않는다
- SPEC에 없는 결정은 임의로 하지 않고 질문한다
- 기존 엔드포인트는 수정하지 않고 신규 엔드포인트만 추가한다
- 스키마 변경(schema.sql, models/__init__.py) 전 팀원 공유 후 진행한다

---

## I-00: Phase 2 Railway 배포

**Status**: 진행 전

**대응 Tasks**: T-00

**결과**: (작업 후 기입)

---

## I-01: DB 구조 고도화 (Inventory + Story + 소프트 딜리트 + FULLTEXT)

**Status**: 진행 전

**대응 Tasks**: T-01, T-02, T-03, T-04

**결과**: (작업 후 기입)

---

## I-02: PriceHistory 연동

**Status**: 진행 전

**대응 Tasks**: T-05

**결과**: (작업 후 기입)

---

## I-03: 점포·시장 상세 API

**Status**: 진행 전

**대응 Tasks**: T-06

**결과**: (작업 후 기입)

---

## I-04: 상인 드랍 관리 API

**Status**: 진행 전

**대응 Tasks**: T-07

**결과**: (작업 후 기입)

---

## I-05: 상품 수정·삭제 API

**Status**: 진행 전

**대응 Tasks**: T-08

**결과**: (작업 후 기입)

---

## I-06: 장보기 에이전트

**Status**: 진행 전

**대응 Tasks**: T-09

**결과**: (작업 후 기입)

---

## I-07: 동선 알고리즘 개선

**Status**: 진행 전

**대응 Tasks**: T-10

**결과**: (작업 후 기입)

---

## I-08: Operator CatalogItem API

**Status**: 진행 전

**대응 Tasks**: T-11

**결과**: (작업 후 기입)

---

## I-09: 캐싱 + Rate Limiting + Health Check

**Status**: 진행 전

**대응 Tasks**: T-12, T-13, T-14

**결과**: (작업 후 기입)

---

## I-10: 테스트 보강 + OpenAPI 문서 완성

**Status**: 진행 전

**대응 Tasks**: T-15, T-16

**결과**: (작업 후 기입)
