# 전통시장 서비스 MVP DB 구축 보고서

## 1. 개요

| 항목 | 내용 |
|------|------|
| 작업 목적 | 전통시장 소비자·상인 연결 서비스 MVP 데이터베이스 설계 및 스키마 구축 |
| 작업 일시 | 2026-04-18 |
| 환경 | macOS (Homebrew), MySQL 8.0, Python 3.11+ |

전통시장 디지털화를 목표로 하는 MVP 서비스의 핵심 데이터 구조를 정의합니다.
소비자의 장보기 계획, 상인의 상품/드랍 관리, 운영자의 시장 관리를 지원하는
12개 테이블로 구성됩니다.

---

## 2. 데이터베이스 구성

### 기본 설정

| 항목 | 값 |
|------|----|
| DB명 | `market_mvp` |
| 문자셋 | `utf8mb4` |
| 콜레이션 | `utf8mb4_unicode_ci` |
| 스토리지 엔진 | `InnoDB` |
| 공통 필드 | `created_at DATETIME DEFAULT CURRENT_TIMESTAMP` |

### 테이블 목록

| # | 테이블명 | 역할 |
|---|----------|------|
| 1 | Market | 전통시장 기본 정보 및 위치 저장 |
| 2 | User | 소비자·상인·운영자 계정 관리 |
| 3 | Store | 시장 내 개별 점포 정보 |
| 4 | Merchant | 점포 운영 상인과 User 연결 |
| 5 | Product | 점포별 판매 상품 목록 및 재고 상태 |
| 6 | DropEvent | 상품 입고 예정 및 한정 판매 이벤트 |
| 7 | CatalogItem | 시장 단위 카탈로그 스냅샷 (드랍/상품/이벤트) |
| 8 | ShoppingList | 사용자 장보기 목록 |
| 9 | ShoppingListItem | 장보기 목록 내 개별 품목 |
| 10 | RoutePlan | 사용자별 시장 방문 동선 계획 (JSON) |
| 11 | Notification | 사용자 알림 (입고, 드랍, 이벤트 등) |
| 12 | Preorder | 상품 사전 주문 / 예약 구매 요청 |

---

## 3. 엔터티별 데이터 현황

| # | 테이블명 | mock row 수 | real row 수 | 소스 구분 | 비고 |
|---|----------|:-----------:|:-----------:|-----------|------|
| 1 | Market | 1 | - | 모킹 / 실데이터 | `market_collect.py` 수집 후 실데이터 대체 예정 |
| 2 | User | 5 | - | 모킹 | consumer 2, merchant 2, operator 1 |
| 3 | Store | 10 | - | 모킹 | 망원시장 내 10개 점포 |
| 4 | Merchant | 10 | - | 모킹 | Store 1개당 1명 매핑 |
| 5 | Product | 48 | - | 모킹 | 점포당 4~5개, 실 시세 기반 |
| 6 | DropEvent | 12 | - | 모킹 | 오늘·내일 혼합, 07:00~11:00 |
| 7 | CatalogItem | 18 | - | 모킹 | drop 8 / product 7 / event 3 |
| 8 | ShoppingList | 3 | - | 모킹 | consumer 2명 소유 |
| 9 | ShoppingListItem | 15 | - | 모킹 | 리스트당 5개 |
| 10 | RoutePlan | 3 | - | 모킹 | 3~5개 점포 경유, JSON 경로 포함 |
| 11 | Notification | 6 | - | 모킹 | 4가지 type, is_read 혼합 |
| 12 | Preorder | 2 | - | 모킹 | Phase2 시나리오 샘플 |

> **범례** — 모킹: `data/mock/` JSON 파일 기반 / 실데이터: 외부 API 수집 (`market_collect.py`, `kamis_collect.py`)  
> real row 수는 `seed_real.py` 실행 후 갱신 예정.

---

## 4. 테이블 관계도 (텍스트 ERD)

```
Market (1) ──────────────────────────────< (N) Store
  │                                              │
  │                                              ├──< (N) Merchant ──> (1) User
  │                                              │
  │                                              ├──< (N) Product
  │                                              │         │
  │                                              │         └──< (N) DropEvent
  │                                              │
  │                                              └──< (N) Preorder ──> (1) User
  │
  ├──< (N) CatalogItem
  │
  └──< (N) RoutePlan ──────────────────────────> (1) User

User (1) ──< (N) ShoppingList (1) ──< (N) ShoppingListItem
User (1) ──< (N) Notification
```

### 관계 요약

| 부모 테이블 | 자식 테이블 | 관계 |
|-------------|-------------|------|
| Market | Store | 1 : N |
| Market | CatalogItem | 1 : N |
| Market | RoutePlan | 1 : N |
| User | Merchant | 1 : N |
| User | ShoppingList | 1 : N |
| User | RoutePlan | 1 : N |
| User | Notification | 1 : N |
| User | Preorder | 1 : N |
| Store | Merchant | 1 : N |
| Store | Product | 1 : N |
| Store | DropEvent | 1 : N |
| Store | Preorder | 1 : N |
| Product | DropEvent | 1 : N |
| ShoppingList | ShoppingListItem | 1 : N |

---

## 5. 주요 필드 정의 요약

### Market
- **PK**: `market_id VARCHAR(36)`
- **주요 필드**: `lat DECIMAL(10,7)`, `lng DECIMAL(10,7)`

### User
- **PK**: `user_id VARCHAR(36)`
- **ENUM**: `role` — `consumer` / `merchant` / `operator`

### Store
- **PK**: `store_id VARCHAR(36)`
- **FK**: `market_id → Market.market_id`
- **주요 필드**: `zone_label` (구역 라벨, 예: A구역)

### Merchant
- **PK**: `merchant_id VARCHAR(36)`
- **FK**: `store_id → Store.store_id`, `user_id → User.user_id`

### Product
- **PK**: `product_id VARCHAR(36)`
- **FK**: `store_id → Store.store_id`
- **ENUM**: `stock_status` — `in_stock` / `low_stock` / `out_of_stock`

### DropEvent
- **PK**: `drop_id VARCHAR(36)`
- **FK**: `product_id → Product.product_id`, `store_id → Store.store_id`
- **ENUM**: `status` — `scheduled` / `arrived` / `sold_out`

### CatalogItem
- **PK**: `catalog_item_id VARCHAR(36)`
- **FK**: `market_id → Market.market_id`
- **ENUM**: `item_type` — `drop` / `product` / `event`
- **스냅샷 필드**: `title_snapshot`, `image_snapshot`, `price_snapshot`

### ShoppingList
- **PK**: `shopping_list_id VARCHAR(36)`
- **FK**: `user_id → User.user_id`

### ShoppingListItem
- **PK**: `list_item_id VARCHAR(36)`
- **FK**: `shopping_list_id → ShoppingList.shopping_list_id`
- **주요 필드**: `product_name_snapshot`, `qty`, `unit`, `checked TINYINT(1)`

### RoutePlan
- **PK**: `route_plan_id VARCHAR(36)`
- **FK**: `user_id → User.user_id`, `market_id → Market.market_id`
- **주요 필드**: `route_json JSON` (MySQL 8.0 네이티브 JSON 타입)

### Notification
- **PK**: `notification_id VARCHAR(36)`
- **FK**: `user_id → User.user_id`
- **주요 필드**: `type`, `target_type`, `target_id`, `is_read TINYINT(1)`

### Preorder
- **PK**: `preorder_id VARCHAR(36)`
- **FK**: `user_id → User.user_id`, `store_id → Store.store_id`
- **ENUM**: `status` — `requested` / `confirmed` / `ready` / `cancelled`

---

## 6. Phase별 구현 범위

### P0 — 현재 구현 완료 (스키마 정의 완료)

- [x] Market, Store, Product 기본 구조
- [x] User 역할 기반 설계 (consumer / merchant / operator)
- [x] Merchant — Store ↔ User 연결 테이블
- [x] DropEvent 입고 이벤트 구조
- [x] ShoppingList + ShoppingListItem 장보기 목록
- [x] Notification 알림 테이블
- [x] CatalogItem 카탈로그 스냅샷 구조

### P1 — 다음 단계 예정

- [ ] UUID 자동 생성 트리거 또는 앱 레이어 적용
- [ ] Product 검색을 위한 FULLTEXT INDEX 추가
- [ ] DropEvent 알림 자동화 (트리거 또는 스케줄러)
- [ ] RoutePlan JSON 스키마 검증 로직
- [ ] KAMIS 가격 데이터 연동 및 Product 가격 자동 업데이트
- [ ] 인덱스 최적화 (market_id, store_id, user_id 복합 인덱스)

### P2 — 스키마만 준비된 항목

- [ ] **Preorder**: 사전 주문 흐름 (요청 → 확인 → 준비 → 취소) 스키마 정의 완료,
  결제·정산 연동은 P2 이후 설계 예정

---

## 7. 모킹 데이터 시나리오 설계 기준

### 배경 설정

망원시장(서울시 마포구)을 배경으로 실제 전통시장 운영 패턴을 반영해 설계했습니다.

### 업종 구성 비율 (Store 10개)

| 업종 | 점포 수 | 비율 | 해당 점포 |
|------|:-------:|:----:|-----------|
| 야채 | 2 | 20% | 망원 신선야채, 망원 채소마트 |
| 과일 | 2 | 20% | 망원 과일나라, 달콤 과일 |
| 수산 | 2 | 20% | 망원 수산, 신선 해산물 |
| 정육 | 1 | 10% | 망원 정육 |
| 반찬 | 1 | 10% | 망원 반찬가게 |
| 잡화 | 1 | 10% | 망원 생활잡화 |
| 건어물 | 1 | 10% | 망원 건어물 |

> 전통시장 실제 업종 분포 참고: 신선식품(야채·과일·수산·정육) 60%, 가공·기타 40%

### 재고 상태 분포 (Product 48개)

| stock_status | 개수 | 비율 | 설계 의도 |
|--------------|:----:|:----:|-----------|
| `in_stock` | 33 | 69% | 정상 판매 중인 일반 상품 |
| `low_stock` | 10 | 21% | 당일 소진 가능성이 있는 인기 상품 또는 제철 품목 |
| `out_of_stock` | 5 | 10% | 이미 판매 완료된 한정 수량 상품 |

### DropEvent 시간대 설정 기준

| 시간대 | 의미 |
|--------|------|
| 07:00 ~ 08:00 | 새벽 경매·직송 물량 도착 (수산·과일 중심) |
| 08:00 ~ 09:30 | 오전 개장 직후 한정 입고 (정육·야채 중심) |
| 09:30 ~ 11:00 | 오전 중반 특가 드랍 또는 마감 임박 알림 |
| 익일 07:00 ~ 10:00 | 예약 예정 드랍 (`scheduled`) — 사전 알림용 |

- `arrived` (4개): 이미 입고 완료, 현재 구매 가능 상태
- `scheduled` (6개): 오늘·내일 입고 예정, 알림 대상
- `sold_out` (2개): 당일 완판, 재고 소진 시나리오 표현

### User role 구성 (5명)

| role | 수 | 설명 |
|------|:--:|------|
| `consumer` | 2 | 장보기 목록·동선 계획·알림 수신 주체 |
| `merchant` | 2 | 각 5개 점포 운영 (박철수: A·B·A·C·B구역, 최영희: D·C·D·E·E구역) |
| `operator` | 1 | 시장 전체 관리 및 CatalogItem 관리 주체 (Phase 2 활성화 예정) |

### 기타 설계 기준

- **좌표**: 망원시장 중심(37.5556, 126.9104) 기준 반경 50m 이내 랜덤 배치
- **가격**: 2026년 기준 실제 전통시장 시세 ±10% 수준으로 설정
- **ShoppingList**: 소비자 장보기 목적별 분류 (반찬거리 / 제수 준비 / 바비큐)
- **RoutePlan**: 동선 효율을 고려해 인접 구역 순서로 점포 배치

---

## 8. 알려진 제약사항 및 향후 과제

| 항목 | 내용 |
|------|------|
| UUID 관리 | `VARCHAR(36)` PK는 앱 레이어에서 UUID v4 생성 필요 (DB 기본값 없음) |
| 이미지 저장 | `image_url`은 URL 참조 방식; 실제 파일은 외부 스토리지(S3 등) 사용 필요 |
| JSON 유효성 | `route_json` 컬럼은 MySQL JSON 타입으로 문법 검증만 수행; 스키마 검증은 앱 레이어 담당 |
| 소프트 딜리트 | 현재 물리 삭제 방식; 향후 `deleted_at` 컬럼 추가 검토 필요 |
| 결제 테이블 | Preorder 결제·정산을 위한 Payment 테이블은 미포함 (P2 범위) |
| 이력 관리 | 가격 변경 이력을 위한 ProductPriceHistory 테이블 추가 검토 필요 |
| 인덱스 | MVP 단계로 PK/FK 외 별도 인덱스 미정의; 쿼리 패턴 확정 후 추가 예정 |

---

## 9. 명세서 변경 이력

### 9.1 변경 배경

2026-04-20, 팀 합의를 통해 MVP 구현 범위에서 **관리자(Admin) 역할** 및 **운영 대시보드(FR-A-03)** 를 제외하기로 결정하였습니다. 이에 따라 기능명세서, UI/UX 명세서, ERD 문서를 수정하고 GitHub에 반영하였습니다.

### 9.2 변경 상세 내역

| 파일 | 위치 | 변경 전 | 변경 후 |
|------|------|---------|---------|
| Fuctional_Specification.md | §3.1 인스코프 공통 | 운영 대시보드(기본 모니터링) 포함 | 항목 삭제 |
| Fuctional_Specification.md | §3.1 공통 — 인증 역할 | (소비자/상인/관리자) | (소비자/상인) |
| Fuctional_Specification.md | §4.1 페르소나 | P5(운영): 지자체/시장 운영 관리자 | 항목 삭제 |
| Fuctional_Specification.md | §4.2 사용자 목표 | 관리자: 시장 활성화 지표를 데이터로 확인 | 항목 삭제 |
| Fuctional_Specification.md | §5.3 FR-A-03 | 운영 대시보드 KPI 섹션 전체 | 섹션 삭제 |
| Fuctional_Specification.md | §5.3 FR-A-01 역할 | 소비자, 상인, 관리자 | 소비자, 상인 |
| UIUX_Speification.md | §3.1 사용자 유형 | 소비자 / 상인 / 관리자(Admin) | 소비자 / 상인 |
| UIUX_Speification.md | §3.2 접근 정책 | 관리자: 운영 대시보드(웹/관리 콘솔 별도) | 항목 삭제 |
| UIUX_Speification.md | §7 SCR-M-01 연계 기능 | FR-A-03 (삭제된 기능 참조) | FR-M-01 |
| UIUX_Speification.md | §15 오픈 이슈 4번 | 관리자 대시보드 UI 범위 확정 필요 | 항목 삭제 |
| ERD.md | §3 엔터티 목록 | Preorder 포함 (Phase 2 표기) | Preorder 행 삭제 |
| ERD.md | §4 엔터티 정의 | DropEvent 정의 블록 누락 | 정의 블록 복원 |
| ERD.md | §5 엔터티 관계 | Store 1:N DropEvent 관계 누락 | 관계 복원 및 번호 재정렬 |

### 9.3 DB 스키마 영향 분석

| 항목 | 영향 여부 | 비고 |
|------|:---------:|------|
| schema.sql | 없음 | Preorder 테이블은 이미 Phase 2로 분리 설계됨 |
| seed_mock.py | 없음 | 모킹 데이터 변경 불필요 |
| seed_real.py | 없음 | 실데이터 적재 로직 변경 없음 |
| User.role ENUM | 유지 결정 | `operator` ENUM 값 유지 — MVP에서는 기능 없음. Phase 2 관리자 콘솔 구현 시 활성화 예정. 스키마 변경 불필요 |

### 9.4 후속 조치

- API 설계 시 관리자 전용 엔드포인트 제외
- `User.role` ENUM의 `operator` 값은 Phase 2까지 유지 (스키마 변경 없음)
- 운영 대시보드 및 관리자 콘솔은 Phase 2 명세서 작성 시 재정의

---

## 10. 실행 명령어 요약

DB 초기화부터 검증까지 전체 재현 순서입니다.

### 사전 준비

```bash
# 1. MySQL 8.0 설치 확인 (Homebrew)
brew services list | grep mysql

# 2. MySQL 시작 (중지 상태인 경우)
brew services start mysql

# 3. 의존 패키지 설치
pip install mysql-connector-python

# 4. 환경변수 설정
cp market-mvp/.env.example market-mvp/.env
# .env 파일에 DB_USER, DB_PASSWORD, SEOUL_API_KEY 등 입력
```

### DB 스키마 생성

```bash
# 5. schema.sql 실행 — DB 생성 + 전체 테이블 생성
mysql -u root -p < market-mvp/db/schema.sql

# 6. 생성 확인
mysql -u root -p -e "USE market_mvp; SHOW TABLES;"
```

### 데이터 수집 (실데이터)

```bash
# 7. 서울 열린데이터광장에서 망원시장·통인시장 수집
#    → data/real/markets.json 생성
python market-mvp/scripts/market_collect.py

# 8. KAMIS 농산물 가격 데이터 수집
#    → data/real/kamis_prices_YYYYMMDD.json 생성
python market-mvp/scripts/kamis_collect.py
```

### 데이터 적재

```bash
# 9. 모킹 데이터 적재 (개발·테스트용)
#    data/mock/*.json → market_mvp DB
python market-mvp/scripts/seed_mock.py

# 10. 실데이터 적재 (수집 완료 후)
#     data/real/*.json → market_mvp DB
python market-mvp/scripts/seed_real.py
```

### 검증

```bash
# 11. DB 검증 — 7개 항목 조회 및 출력
python market-mvp/scripts/verify.py
```

### 전체 초기화 (재설치 시)

```bash
# 주의: 기존 데이터 전체 삭제
mysql -u root -p -e "DROP DATABASE IF EXISTS market_mvp;"
mysql -u root -p < market-mvp/db/schema.sql
python market-mvp/scripts/seed_mock.py
python market-mvp/scripts/verify.py
```

---

> 작성자: 운영팀 | 버전: v0.2.0 (2026-04-20 — MVP 범위 확정 반영)
