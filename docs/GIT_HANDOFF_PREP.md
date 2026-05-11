# Git 공유 준비 가이드 (PR 전 단계)

## 목적
이 문서는 **아직 PR은 열지 않고**, 팀원과 충돌을 최소화한 상태로 작업물을 공유하기 위한 준비 절차입니다.

---

## 1) 현재 작업 브랜치
- 현재 브랜치: `story+shopping-agent-0425`
- 상태: 다수 파일 변경 + 신규 파일 존재

---

## 2) 공유 방식 원칙 (충돌 최소화)
1. 한 번에 전부 올리지 않고, **주제별 커밋으로 분할**
2. `서버/클라/데이터/문서`를 분리해 커밋
3. 팀원 핵심 변경 파일과 충돌 가능성이 높은 파일은 별도 커밋으로 분리
4. PR 전 `main` 최신화(rebase/merge) 후 테스트
5. 데이터 연동 원칙: **팀원 담당 기능은 팀원 모킹데이터**, 그 외는 **내 모킹데이터** 기준으로 유지

---

## 3) 권장 커밋 묶음 (순서대로)

## A. 문서 커밋
- `docs/TEAM_HANDOFF_A_TO_Z.md`
- `docs/GIT_HANDOFF_PREP.md`
- `docs/Mock_Data_Execution_Guide.md` (필요 시)

커밋 예시:
```bash
git add docs/TEAM_HANDOFF_A_TO_Z.md docs/GIT_HANDOFF_PREP.md docs/Mock_Data_Execution_Guide.md
git commit -m "docs: add team handoff and git prep guide"
```

## B. 스토리/가격 연동 프론트 커밋
- `client/lib/core/network/api_client.dart`
- `client/lib/features/merchant/merchant_story_screen.dart`
- `client/lib/features/merchant/merchant_story_list_screen.dart`
- `client/lib/features/merchant/merchant_price_history_screen.dart`
- `client/lib/features/home/store_public_story_screen.dart`
- `client/lib/app/router.dart`
- `client/lib/features/merchant/merchant_dashboard_screen.dart`
- `client/lib/features/home/spotlight_screen.dart`

커밋 예시:
```bash
git add client/lib/core/network/api_client.dart \
  client/lib/features/merchant/merchant_story_screen.dart \
  client/lib/features/merchant/merchant_story_list_screen.dart \
  client/lib/features/merchant/merchant_price_history_screen.dart \
  client/lib/features/home/store_public_story_screen.dart \
  client/lib/app/router.dart \
  client/lib/features/merchant/merchant_dashboard_screen.dart \
  client/lib/features/home/spotlight_screen.dart
git commit -m "feat(client): integrate persistent story and price history flow"
```

## C. 디자인/UI 고도화 커밋
- `client/lib/features/auth/login_screen.dart`
- `client/lib/features/common/consumer_shell_screen.dart`
- `client/lib/features/drop/drop_list_screen.dart`
- `client/lib/features/home/home_screen.dart`
- `client/lib/features/home/event_screen.dart`
- `client/lib/features/route/route_screen.dart`
- `client/lib/features/search/search_screen.dart`
- `client/lib/features/shopping/agent_screen.dart`
- `client/assets/images/**`
- `client/lib/features/route/widgets/**`
- `client/lib/shared/utils/**`
- `client/pubspec.yaml`, `client/web/index.html`

## D. 데이터/스크립트 커밋
- `data/mock/products.json`
- `data/mock/stores.json`
- `data/mock/profiles/**`
- `scripts/seed_mock.py`
- `scripts/seoul_price_collect.py`
- `scripts/generate_products_from_prices.py`

데이터 커밋 규칙:
- 팀원 담당 기능 경로/파일 변경은 허용
- 내 담당 기능은 `my_demo` 기준 데이터 유지
- 커밋 메시지에 데이터 기준을 명시
  - 예: `data: sync teammate profile for story backend integration`
  - 예: `data: update my_demo products for consumer search/drop`

## E. 서버 고도화 커밋
- `server/app/services/story_service.py`
- `server/app/services/shopping_agent_service.py`
- `server/app/core/config.py`

---

## 4) 절대 올리지 말아야 할 파일
- `server/local_demo.db` (로컬 개발 DB)
- 개인 키/비밀번호가 담긴 `.env`류 파일

확인 명령:
```bash
git status --short
```
`server/local_demo.db`가 보이면 add 제외.

---

## 5) 팀원과 충돌 위험 높은 파일
아래 파일은 팀원이 동시에 수정했을 가능성이 높아, 공유 전 diff 설명이 필요:
- `client/lib/core/network/api_client.dart`
- `client/lib/app/router.dart`
- `server/app/services/story_service.py`
- `server/app/services/shopping_agent_service.py`
- `scripts/seed_mock.py`

권장: 위 파일은 커밋 메시지에 “왜 수정했는지”를 1줄 명시.

---

## 6) PR 직전 체크리스트
1. `main` 최신 반영
```bash
git fetch origin
git checkout main
git pull origin main
git checkout story+shopping-agent-0425
git rebase main
```

2. 실행 확인
- 서버 health: `GET /health`
- 로그인
- 검색 결과
- 드랍 리스트
- 장보기 에이전트
- 상인 스토리 생성/게시

3. 충돌 해결 후 재검증

---

## 7) 핵심 요약
- PR 전에 준비할 것은 "코드 정리"보다 **커밋 분리 + DB 일치 + 충돌 파일 설명**
- 병합 실패 원인의 대부분은 기능 자체가 아니라 **환경/데이터 불일치**
