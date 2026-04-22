# Market Info — Backend (server/)

## 프로젝트 개요

**마켓인포(Market Info)** 는 전통시장 상품 정보와 점포 콘텐츠를 디지털로 제공하는 서비스다.
소비자의 장보기 행동을 전통시장 방문으로 전환하는 것이 핵심 목표다.

- 홈 화면은 방문 유도 허브(드랍/행사/점포 스포트라이트)로 운영한다.
- DropEvent(입고 알림)가 MVP 핵심 기능이며 방문 트리거 역할을 한다.
- 상인 등록은 수동 입력과 AI draft 두 경로를 모두 지원한다.

## 참조 문서

| 문서 | 경로 |
|------|------|
| 백엔드 실행 계획서 | `../docs/Backend_Execution_Plan.md` |
| API 명세서 | `../docs/API_Specification.md` |
| ERD | `../docs/ERD.md` |
| DB 구축 보고서 | `../docs/db_setup_report.md` |
| 기능명세서 | `../docs/Fuctional_Specification.md` |
| UI/UX 명세서 | `../docs/UIUX_Speification.md` |

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.11+ |
| 프레임워크 | FastAPI |
| DB | MySQL 8.0 (`market_mvp`) |
| ORM | SQLAlchemy |
| DB 드라이버 | PyMySQL |
| 인증 | JWT (이메일/비밀번호, 소셜 로그인은 MVP 이후) |
| 문자셋 | utf8mb4 / utf8mb4_unicode_ci |

## 백엔드 폴더 구조

```
server/
  app/
    main.py              # FastAPI 앱 진입점
    core/                # config, security, exception 핸들러
    db/                  # session, models, repositories
    schemas/             # request/response DTO (Pydantic)
    services/            # 비즈니스 로직
    api/
      v1/                # 라우트 모듈 (auth, home, products, drops, ...)
  tests/                 # 단위·통합 테스트
```

## API 규약

- Base URL: `/api/v1`
- 공통 응답 형식

```json
{
  "success": true,
  "code": "OK",
  "message": "요청이 성공했습니다.",
  "data": {},
  "meta": { "request_id": "req_xxx", "timestamp": "..." }
}
```

- 페이지네이션: `page`(기본 1), `size`(기본 20, 최대 100)
- `user_id`는 항상 JWT에서 추출하며 Request body/Query로 받지 않는다.

## 핵심 도메인 규칙

### ENUM 값 (DB와 1:1 고정)

| 필드 | 허용값 |
|------|--------|
| `User.role` | `consumer` / `merchant` / `operator` |
| `Product.stock_status` | `in_stock` / `low_stock` / `out_of_stock` |
| `DropEvent.status` | `scheduled` / `arrived` / `sold_out` |
| `CatalogItem.item_type` | `drop` / `event` / `store_spotlight` |
| `Notification.target_type` | `product` / `drop` / `preorder` / `store` |

### 비즈니스 규칙

- `User.role = operator`는 DB에 존재하지만 MVP API에서 비활성 상태다.
- DropEvent 상태 변경 시 구독자에게 알림을 트리거한다.
- 알림 실패 시 인앱 대체 + 1회 재시도 상태를 기록한다.
- 지도 데이터 불완전 시 `zone_label`을 반드시 응답에 포함한다.
- AI 응답 실패 시 `fallback_mode=true`로 수동 입력 전환한다.
- Preorder API는 현재 비활성(DB만 존재)이다.
- 결제/정산 API는 MVP 미구현 범위다.

## DB 핵심 테이블

`Market` · `User` · `Store` · `Merchant` · `Product` · `DropEvent` · `CatalogItem` · `ShoppingList` · `ShoppingListItem` · `RoutePlan` · `Notification` · `Preorder`(Phase 2)

- PK 타입: `VARCHAR(36)`, 앱 레이어에서 UUID v4 생성
- `RoutePlan.route_json`: MySQL JSON 네이티브 타입, 스키마 검증은 앱 레이어 담당
- `ShoppingListItem.product_name_snapshot`: 기본 표시값, product_id 연결은 옵션

## 환경 설정

```bash
# .env 파일 (루트)
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=3306
DB_NAME=market_mvp
SECRET_KEY=...
SEOUL_API_KEY=...   # 공공데이터
```

## 테스트 전략

- 단위 테스트: `services/` 계층
- 통합 테스트: 라우터 + 실 DB (mock DB 사용 금지)
- 계약 테스트: `../docs/API_Specification.md` 응답 키 비교
