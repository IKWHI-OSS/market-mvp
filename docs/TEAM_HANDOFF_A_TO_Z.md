# Market MVP 통합 핸드오프 (A to Z)

## 1) 문서 목적
이 문서는 팀 병합 시 충돌을 줄이고, 백엔드/프론트엔드/DB 연동을 안정적으로 맞추기 위한 **최종 작업 요약 + 운영 가이드**입니다.  
특히 이번 작업에서 반복적으로 발생한 이슈(서버는 정상이나 DB 비연동, 로컬/레일웨이 DB 혼용, 화면 데이터 공백)를 방지하는 데 초점을 둡니다.

---

## 2) 현재 기준 아키텍처 (작동 구조)
- Client: Flutter Web (`client/`)
- Server: FastAPI (`server/`)
- DB: MySQL (Railway)
- AI: Anthropic API (스토리 생성, 장보기 에이전트)
- 지도: Naver Map (시장 중심 좌표/핀 표시)
- 데이터: 공공데이터 + 모킹데이터 혼합

### 호출 흐름
1. Flutter → `API_BASE_URL`로 FastAPI 호출  
2. FastAPI → `DATABASE_URL` 기준으로 DB 조회/쓰기  
3. 스토리/장보기 에이전트는 Anthropic 호출 (실패 시 폴백 로직 일부 적용)  
4. 응답 데이터는 화면 단에서 카드/리스트/상세로 렌더링

---

## 3) 가장 중요한 병합 주의사항 (DB/ENV)

## 3.1 핵심 원칙
- **서버와 시딩 대상 DB가 반드시 동일해야 함**
- `server/.env`의 `DATABASE_URL`과 시딩 스크립트 연결 DB가 다르면, 화면은 뜨지만 데이터가 비어 보임
- 로컬 SQLite와 Railway MySQL을 혼용하지 말 것

## 3.2 필수 점검 순서
1. `server/.env` 확인
- `DATABASE_URL=mysql+mysqlconnector://...` (Railway)
- `SECRET_KEY=...`
- `ANTHROPIC_API_KEY=...`
- `ANTHROPIC_MODEL_STORY=...`
- `ANTHROPIC_MODEL_SHOPPING_AGENT=...`

2. DB 시딩
- `python3 scripts/seed_mock.py --profile agent_demo`
- 시딩 완료 로그에서 Product/DropEvent/Store/ShoppingList 반영 건수 확인

3. 서버 실행 후 API 검증
- `/health`
- `/api/v1/drops?...`
- `/api/v1/products/search?...`

4. 클라이언트 실행
- `--dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1`

## 3.3 자주 발생한 장애와 원인
- 증상: 검색/드랍/에이전트 결과 없음  
  원인: DB 비시딩 또는 서버가 다른 DB 참조
- 증상: 로그인은 되는데 기능 결과가 비정상  
  원인: 서버는 살아있지만 실데이터가 없는 DB 연결
- 증상: 포트 충돌(8000/5179)  
  원인: 이전 프로세스 미종료

---

## 4) 이번 개발에서 반영된 핵심 작업 요약

## 4.1 공통/플랫폼
- 서비스명/브랜딩 업데이트 (돗개비)
- 로고 교체/크기/정렬/화면별 적용 통일
- 에러 UX 문구 한국어화 및 fallback 경로 정리

## 4.2 소비자 영역
- 홈(SCR-C-01): 드랍 중심 진입 구조 강화, 이벤트/점포 유입형 CTA 정리
- 검색(SCR-C-02): 검색 결과 카드 시각 정리, BEST 카드/동선 진입 연계
- 상세(SCR-C-03): 가격 표기 통일(₩), 불필요 문구 정리
- 드랍(SCR-C-04): 상태/탭/알림 동작 정리
- 장보기 에이전트(SCR-C-05): 추천 응답 구조 개선, 입력/출력 UX 개선
- 장보기 리스트(SCR-C-06): 체크/상태 표시, UI 정리
- 장보기 동선(SCR-C-07): 방문 플로우 개선, 지도 영역 개선
- 이벤트/점포 상세/마이페이지: 가상화면 포함 구성 정리

## 4.3 상인 영역
- 상인 홈(SCR-M-01): 로그인 사용자명 반영, 섹션 네이밍 개선
- 상품 등록/검토(SCR-M 계열): 플로우 정리 및 AI 보조 동선 정리
- 상인 스토리 생성 에이전트: 프롬프트 기반 생성 + 게시 플로우 개선

## 4.4 AI/데이터 고도화
- Anthropic 연동(스토리/장보기)
- 모킹데이터 대량 보강 (시장/점포/상품/드랍 등)
- 공공 가격 데이터(서울시농수산식품공사 주요품목가격) 기반 상품 대량 생성 파이프라인 구성

---

## 5) 화면별 기능 현황 및 구현 수준

## 5.1 소비자 화면
- SCR-A-1 로그인
  - 상태: 구현 완료
  - 비고: 에러 문구 한국어화, 라우팅 안정화

- SCR-C-01 홈
  - 상태: 구현 완료(고도화)
  - 핵심: 드랍/이벤트/점포 유입형 구성, CTA 기반 이동

- SCR-C-02 검색 결과
  - 상태: 구현 완료(개선 필요 일부)
  - 핵심: 카드 기반 비교, 동선 추가 유도
  - 주의: 검색 정밀도(연관도 필터)는 추가 튜닝 여지 존재

- SCR-C-03 점포/상품 상세
  - 상태: 구현 완료
  - 핵심: 가격/상세/점포 연결

- SCR-C-04 드랍 리스트
  - 상태: 구현 완료
  - 핵심: 드랍 상태별 표시/알림 연동

- SCR-C-05 장보기 에이전트
  - 상태: 구현 완료(실 AI 호출 기반)
  - 핵심: 질의 → 재료 추천 → 점포 매칭
  - 주의: 데이터 품질에 따라 결과 품질 변동

- SCR-C-06 장보기 리스트
  - 상태: 구현 완료
  - 핵심: 체크/수량/상태 기반 리스트

- SCR-C-07 장보기 동선
  - 상태: 구현 완료(지도 표시)
  - 핵심: 방문 리스트 + 지도 핀
  - 주의: 지도 조작 정책(줌 제한 vs 핀 고정)은 운영 정책 확정 필요

- 이벤트/점포 스포트라이트/마이페이지
  - 상태: 구현 완료(일부 가상/모킹 구성)
  - 주의: 실제 운영 전 사용자 데이터 기반 치환 필요

## 5.2 상인 화면
- SCR-M-01 상인 홈
  - 상태: 구현 완료
  - 핵심: 로그인 사용자명 반영, 관리도구 진입

- 상인 스토리 생성 화면
  - 상태: 구현 완료(실 AI 호출)
  - 핵심: 소개문 입력, 톤/길이, 결과 생성/게시
  - 보완: 생성문 품질 튜닝(프롬프트/후처리)

- 상인 상품 등록/검토
  - 상태: 구현 완료(일부 항목은 모킹 중심)
  - 보완: 이미지 인식/OCR 연동은 향후 확장

---

## 6) 백엔드-프론트 연결 명세 (핵심)

## 6.1 인증
- 로그인 성공 시 `access_token` 저장
- 이후 요청은 `Authorization: Bearer <token>` 헤더 필요

## 6.2 주요 연동 엔드포인트
- Auth: `/api/v1/auth/login`
- Home/Search:
  - `/api/v1/home`
  - `/api/v1/products/search`
  - `/api/v1/products/{id}`
- Drop:
  - `/api/v1/drops`
  - `/api/v1/drops/{drop_id}/subscribe`
- Shopping Agent:
  - `/api/v1/shopping-agent/recommendations`
- Stories (영구저장/게시):
  - `GET /api/v1/merchant/stories`
  - `GET /api/v1/merchant/stories/{story_id}`
  - `PATCH /api/v1/merchant/stories/{story_id}/publish`
  - `DELETE /api/v1/merchant/stories/{story_id}`
  - `GET /api/v1/stores/{store_id}/story`
- Price History:
  - `GET /api/v1/merchant/products/{product_id}/price-history`

## 6.3 이번 프론트 반영 포인트
- `ApiClient`에 story/price-history 메서드 추가
- `MerchantStoryData` 확장(`storyId`, `isPublished`, `publishedAt`)
- 게시 버그 수정: 스토리 재생성 대신 publish 토글
- 신규 화면 추가:
  - 상인 스토리 리스트
  - 가격 이력 화면
  - 점포 공개 스토리 화면

---

## 7) 기능별 팀 작업 분담/연동 주의

## 7.1 팀원(백엔드) 작업 축
- 상인 스토리 영구저장 테이블/라우트 확장
- 가격 정책 관련 시세 데이터 시드
- 대규모 모킹 및 스토리 데이터 적재
- fallback 동작 보강

## 7.2 내 작업(프론트+연동) 축
- 소비자/상인 핵심 화면 고도화
- AI 기능 UX 및 라우팅 연계
- ApiClient 확장 + 신규 화면 반영
- 모킹데이터/이미지 연동, 지도 연동

## 7.3 병합 시 충돌 위험 지점
- `client/lib/core/network/api_client.dart`
- `client/lib/app/router.dart`
- `client/lib/features/merchant/*`
- `client/lib/features/home/spotlight_screen.dart`
- `server/.env` 및 DB 참조 경로

## 7.4 병합 규칙 권장
1. API 스펙(`docs/API_Specification.md`)을 단일 기준으로 동기화  
2. DB 연결 검증 후 기능 테스트 (로그인→검색→드랍→에이전트→스토리)  
3. PR 단위로 기능 묶음 분리 (스토리/에이전트/지도/UI)

---

## 8) 외부 API/키 사용 현황

## 8.1 사용 API
- Anthropic API
  - 용도: 상인 스토리 생성, 장보기 에이전트 응답 보조
- Naver Map API
  - 용도: 장보기 동선 화면 지도/핀 표시
- 서울 열린데이터광장 API
  - 용도: 농수산 가격 데이터 수집/상품 모킹 생성

## 8.2 환경변수 키 체크리스트
- 서버(`server/.env`)
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `ANTHROPIC_API_KEY`
  - `ANTHROPIC_MODEL_STORY`
  - `ANTHROPIC_MODEL_SHOPPING_AGENT`
- 클라이언트 실행 파라미터
  - `--dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1`

---

## 9) 실행/검증 표준 절차 (팀 공통)

## 9.1 DB 시딩
```bash
cd project/market-mvp
python3 scripts/seed_mock.py --profile agent_demo
```

## 9.2 서버 실행
```bash
cd project/market-mvp/server
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 9.3 클라이언트 실행
```bash
cd project/market-mvp/client
flutter run -d web-server --web-hostname 127.0.0.1 --web-port 5179 \
  --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 9.4 헬스체크
```bash
curl http://127.0.0.1:8000/health
```

---

## 10) 현재 잔여 과제 (병합 후 우선순위)
- 검색 연관도 필터 보강 (비연관 점포 노출 최소화)
- 상인 스토리 생성 결과 후처리(중복/절삭/톤 균질화)
- 가격 이력 시각화(라인차트) 고도화
- 지도 UX 정책 확정(줌/팬 제한, 핀 인터랙션)
- 이미지 에셋/모킹 데이터 매핑 QA
- 배포 환경(Railway)에서 ENV/DB 일치 최종 검증

---

## 11) 모킹데이터 충돌 방지 규칙 (팀 운영 기준)

운영 원칙: **팀원 담당 기능은 팀원 모킹데이터 우선 연동**, 그 외 화면/기능은 **내 모킹데이터 우선 연동**으로 관리한다.

## 11.1 소스 분리
- 개인 작업 데이터는 `data/mock/profiles/<개인프로필>/` 하위에서만 관리
- 공용 `data/mock/*.json` 직접 수정은 최소화
- 본인/팀원 프로필 디렉토리를 명시적으로 분리

## 11.2 시딩 분리
- 본인: `python3 scripts/seed_mock.py --profile my_demo`
- 팀원: `python3 scripts/seed_mock.py --profile teammate_demo`
- 기본은 profile 분리, 단 팀원 담당 기능 검증 시 팀원 profile 사용 허용

## 11.3 DB 분리
- 기본 원칙은 각자 별도 Railway DB 또는 별도 스키마 사용
- 단, 팀원 기능 연동 검증 시 팀원 DB 접속 전환 허용
- 전환 시 `server/.env`의 `DATABASE_URL` 변경 이력(언제/누가/무엇을) 기록
- 공용 배포 DB에는 최종 검증 데이터만 반영

## 11.4 ID 네임스페이스 규칙
- 엔터티 ID prefix를 작업자별로 분리 (`me_*`, `tm_*` 등)
- 이름 중복보다 ID 충돌 방지를 우선

## 11.5 병합 규칙
- 코드 PR과 데이터 PR 분리
- 팀원 담당 기능 범위에서는 팀원 모킹데이터 파일 업데이트 허용
- 내 담당 기능 범위에서는 내 모킹데이터 profile 기준 유지
- 머지 전 공통 스모크 테스트 고정:
  - `/health`
  - `products/search`
  - `drops`
  - `shopping-agent/recommendations`

---

## 12) 결론
현재 상태는 **시연 가능한 MVP+고도화 단계**이며, 핵심 리스크는 기능 자체보다 **DB/ENV 연결 일치**입니다.  
팀 병합 시 API 스펙 단일화 + DB 시딩/헬스체크 루틴만 지키면, 검색/드랍/에이전트/스토리 기능은 안정적으로 재현 가능합니다.
