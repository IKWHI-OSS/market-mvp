# Frontend Execution Plan (Flutter)

## 1. 문서 정보
- 문서명: Market Info 프론트엔드 실행 계획서
- 버전: v1.1
- 작성일: 2026-04-21
- 기술 스택: Flutter (Dart)
- 기준 문서
1. `project/docs/UIUX_Speification.md`
2. `project/docs/Fuctional_Specification.md`
3. `project/docs/API_Specification.md`
4. `project/docs/db_setup_report.md`

## 2. 목표
1. 방문 유도형 홈 UX를 기준으로 MVP 화면을 빠르게 구현
2. DropEvent 카드 경험을 중심으로 2030 사용자 행동 전환 강화
3. API 계약과 화면 모델을 분리해 연동 충돌 최소화
4. 로딩/빈/오류 상태를 모든 핵심 화면에 일관 적용

## 3. 구현 범위
### 3.1 MVP 화면
1. SCR-C-01, SCR-C-02, SCR-C-03, SCR-C-04
2. SCR-C-05, SCR-C-06, SCR-C-07, SCR-C-09, SCR-C-10, SCR-C-11
3. SCR-M-01, SCR-M-02, SCR-M-03
4. SCR-A-01, SCR-A-02

### 3.2 인증 구현 기준 (MVP)
1. 로그인 방식: 이메일/비밀번호 입력
2. 인증 토큰: JWT Bearer 저장 후 API 공통 헤더 주입
3. 역할 분기: JWT의 `role` 기준으로 소비자/상인 홈 라우팅

## 4. 앱 구조
```text
project/client/
  lib/
    app/           # router, app shell
    core/          # network, error, constants
    features/
      auth/
      home/
      search/
      drop/
      shopping/
      route/
      notification/
      merchant/
    shared/widgets/
  test/
```

## 5. UI/상태 기준
1. 홈은 드랍/행사/점포 스포트라이트 중심
2. 검색/상세에서만 상품 상세 강화
3. 상태 enum 고정
1. 재고: `in_stock`, `low_stock`, `out_of_stock`
2. 드랍: `scheduled`, `arrived`, `sold_out`
4. 상태 라벨 매핑(한글): 예정/확정(도착)/마감
5. 오류 시 공통 에러 컴포넌트 사용

## 6. 구현 액션 플랜
### Day 1
1. 앱 라우팅/탭 구성 (기본 진입 SCR-C-01)
2. 공통 컴포넌트 구축 (리스트 카드, 상태 배지, 에러/빈 상태)
3. 홈 허브/드랍 카드 UI 정적 구현

### Day 2
1. 검색/상세/드랍/알림함 API 연동
2. 행사/점포 스포트라이트 상세 구현
3. 로딩/빈/오류 상태 연결

### Day 3
1. 장보기 리스트/동선 화면 연동
2. 상인 등록(입력/결과 검토) 구현
3. AI draft 응답 매핑 + 수동전환 UX 구현

### Day 4
1. 통합 시나리오 테스트
2. 내비게이션/CTA 명세 일치 점검
3. UI 품질 조정(텍스트/간격/배지 일관성)

## 7. API 연동 규칙
1. 화면에서 JSON 직접 사용 금지, DTO→UI Model 변환 필수
2. 응답 키 기준은 `project/docs/API_Specification.md` 고정
3. Optional 필드는 null-safe 처리
4. 요청 실패는 공통 에러 파서 1개로 처리

## 8. 화면별 필수 QA
1. SCR-C-01: 드랍/행사/스포트라이트 노출 및 이동
2. SCR-C-04: 드랍 상태 반영, 구독 토글 반영
3. SCR-C-06: 품목 체크, 동선 이동
4. SCR-C-07: 지도/구역 안내 병행
5. SCR-M-02/03: AI draft→수정→게시

## 9. 완료 기준 (DoD)
1. MVP 대상 화면 CTA/Navigation 100% 동작
2. DropEvent 흐름(조회/상세/구독/알림)이 끊기지 않음
3. API 변경 없이 시연 시나리오 2회 연속 통과
4. 크래시/블로커 버그 0건
