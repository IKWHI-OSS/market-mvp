# Backend Execution Plan (FastAPI + MySQL)

## 1. 문서 정보
- 문서명: Market Info 백엔드 실행 계획서
- 버전: v1.2
- 작성일: 2026-04-21
- 기술 스택: FastAPI, Python 3.11+, MySQL 8.0
- 기준 문서
1. `project/docs/Fuctional_Specification.md`
2. `project/docs/UIUX_Speification.md`
3. `project/docs/ERD.md`
4. `project/docs/db_setup_report.md`

## 2. 목표
1. MVP 핵심 플로우(홈 허브→검색→드랍→알림→리스트→동선→상인등록)를 API로 안정 제공
2. DropEvent를 중심으로 방문 트리거 기능을 우선 완성
3. 프론트와 충돌 없는 응답 스키마/에러 규약 고정
4. AI 보조 등록 실패 시 수동 입력 전환까지 포함

## 3. 구현 범위
### 3.1 MVP API
1. 인증/권한: 소비자/상인 로그인 및 역할 분기 (이메일/비밀번호 + JWT, MVP 시연용 / 소셜 로그인은 MVP 이후 추가)
2. 홈 허브: 드랍 히어로, 행사, 점포 스포트라이트
3. 검색/비교/상세: 상품 + 점포 정보
4. 드랍: 리스트/상태/구독/변경 반영
5. 장보기 리스트: 리스트/아이템 CRUD
6. 동선: 생성/조회
7. 알림함: 목록/읽음 처리
8. 상인 등록: 수동 등록 + AI draft

### 3.2 MVP 구현 이후 추가
1. 장보기 에이전트 고도화 (SCR-C-05, Phase 3)
2. 가격/재고 고도화 (SCR-M-04/05, Phase 2)
3. 상인 스토리 생성 고도화 (SCR-M-06, Phase 2)
4. Preorder 사용자 플로우 (DB만 준비)

## 4. 백엔드 구조
```text
Users/karla/server/
  app/
    main.py
    core/        # config, security, exception
    db/          # session, models, repositories
    schemas/     # request/response DTO
    services/    # business logic
    api/v1/      # route modules
  tests/
```

## 5. 데이터 기준 (db_setup_report 동기화)
1. DB: `market_mvp` (MySQL 8.0)
2. 핵심 테이블: Market, User, Store, Merchant, Product, DropEvent, CatalogItem, ShoppingList, ShoppingListItem, RoutePlan, Notification
3. `User.role ENUM`: `consumer`, `merchant`, `operator` (operator는 Phase 2까지 비활성)
4. DropEvent 상태: `scheduled`, `arrived`, `sold_out`
5. Product 재고: `stock_status` (`in_stock`, `low_stock`, `out_of_stock`) 기준

## 6. 구현 액션 플랜
### Day 1
1. FastAPI 부트스트랩 + DB 연결 + 공통 에러 핸들러
2. 모델/리포지토리 생성 (`schema.sql` 1:1)
3. 인증 API, 홈 API 초안

### Day 2
1. 검색/상세 API 완성
2. 드랍 API(조회/구독) + 알림 생성 연동
3. 알림함 API 구현

### Day 3
1. 장보기 리스트/아이템 API 구현 (장보기 리스트 토대로 `route_json` 생성 알고리즘)
2. 동선 API 구현 (`route_json` 저장/조회)
3. 상인 상품 등록(수동 + AI draft)

### Day 4
1. 통합 테스트 + 성능 점검
2. 실패 시나리오(푸시 실패, AI 실패, 빈데이터) 검증
3. OpenAPI 문서 고정 및 RC 태깅

## 7. 비즈니스 룰 고정
1. 홈은 허브형 노출: 드랍/행사/스포트라이트 우선
2. 드랍 변경 이벤트 발생 시 알림 트리거
3. 알림 실패는 인앱 대체 + 1회 재시도 상태 기록
4. 지도 데이터 불완전 시 `zone_label` 반드시 응답
5. AI 응답 실패 시 `fallback_mode=true`로 수동 입력 전환

## 8. 테스트/검증
1. 단위 테스트: 서비스 계층
2. 통합 테스트: 라우터 + DB
3. 계약 테스트: `project/docs/API_Specification.md` 응답 키 비교
4. E2E 시나리오
1. 소비자: 홈→검색→드랍 구독→알림 확인
2. 상인: 입력→AI draft→검토→게시

## 9. 완료 기준 (DoD)
1. MVP API 경로 구현 완료
2. DropEvent 기반 시연 시나리오 2회 이상 통과
3. 프론트 연동 시 스키마 오류 0건
4. 에러 정책(인앱 대체/재시도/수동전환) 동작 확인
