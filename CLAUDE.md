# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Market Info** — 전통시장 정보 플랫폼 (소비자/상인 양방향 앱)

- **백엔드**: FastAPI + SQLAlchemy + MySQL 8.0 → Railway 자동 배포 (main push 시)
- **프론트**: Flutter Web → GitHub Pages (`gh-pages` 브랜치)
- **베이스 URL**: `https://market-api-production.up.railway.app/api/v1`
- **프론트 URL**: `https://ikwhi-oss.github.io/market-mvp/`

---

## Commands

### Backend (server/)

```bash
# 의존성 설치
cd server
pip install -r requirements.txt --break-system-packages

# 서버 실행 (로컬, .env 필요)
uvicorn app.main:app --reload

# 전체 테스트
python -m pytest tests/ -v

# 단일 테스트 파일
python -m pytest tests/test_preorders.py -v

# 단일 테스트 케이스
python -m pytest tests/test_preorders.py::test_create_preorder -v
```

### Frontend (client/)

```bash
# 웹 빌드
cd client
flutter build web --release --base-href "/market-mvp/"

# gh-pages 배포 (루트에서)
git stash
git checkout gh-pages
cp -r client/build/web/* .
git add -A
git commit -m "deploy: ..."
git push origin gh-pages
git stash pop
git checkout main
```

---

## Architecture

### Backend 구조

```
server/app/
  main.py              # FastAPI 앱, CORS, 예외 핸들러
  core/
    config.py          # Settings (DATABASE_URL, SECRET_KEY 등 .env 로드)
    security.py        # JWT 생성/검증, bcrypt 해싱
    exceptions.py      # 공통 예외 핸들러
  db/
    session.py         # SQLAlchemy engine, Base, get_db()
    models/            # SQLAlchemy ORM 모델 (schema.sql과 1:1)
    repositories/      # DB 쿼리 레이어 (서비스에서만 호출)
  services/            # 비즈니스 로직 (권한 검증 포함)
  api/v1/              # FastAPI 라우터 (라우터는 서비스만 호출)
  schemas/
    common.py          # BaseResponse, success_response()
```

**공통 응답 형식** (모든 엔드포인트 적용):
```json
{
  "success": true,
  "code": "OK",
  "data": {},
  "meta": { "request_id": "req_xxx", "timestamp": "..." }
}
```

**인증**: `Authorization: Bearer <JWT>` — `get_current_user()` Depends로 주입  
**역할**: `consumer` / `merchant` — `user.role.value`로 분기

### Phase 2 추가 기능

| 모듈 | 엔드포인트 | 비고 |
|---|---|---|
| prices.py | `/prices/market/{code}`, `/merchant/dashboard/price-suggestions` | KAMIS 농산물 시세 연동 |
| stories.py | `POST /merchant/stories` | Anthropic Claude LLM, fallback 템플릿 |
| preorders.py | `POST/GET /preorders`, `DELETE /preorders/{id}`, `PATCH /merchant/preorders/{id}/status` | 상태머신: requested→confirmed→ready→cancelled |
| shopping_agent.py | `POST /shopping-agent/recommendations` | 레시피 키워드 매칭 + 점포 상품 연결 |

### 환경변수 (.env)

```
DATABASE_URL=mysql+pymysql://...
SECRET_KEY=...
KAMIS_API_KEY=...        # 없으면 DB fallback
KAMIS_API_ID=...
ANTHROPIC_API_KEY=...    # 없으면 fallback 템플릿
```

### 테스트 규칙

- **SQLite 경로**: 반드시 절대경로 사용 → `sqlite:////tmp/test_xxx.db`
- 상대경로(`sqlite:///./test.db`)는 마운트 파일시스템 I/O 오류 발생
- `scope="module"` fixture로 DB 생성, 테스트 종료 후 `/tmp/test_xxx.db` 삭제

### Frontend 구조

```
client/lib/
  app/router.dart          # AppRoutes 상수 + MaterialPageRoute 매핑
  core/network/api_client.dart  # 싱글턴 HTTP 클라이언트, 모든 API 호출 집중
  features/
    auth/                  # 로그인
    home/                  # 홈, 이벤트, 스포트라이트
    shopping/              # 장보기 에이전트(agent_screen), 장보기 리스트
    merchant/              # 상인 대시보드, 상품 등록, 스토리 생성
    notification/          # 알림함
    search/                # 상품 검색/상세
    route/                 # 동선
```

**인증 상태**: `ApiClient.instance`에 토큰 저장, 모든 요청 헤더에 자동 포함

---

## Key Decisions & Rules

### 브랜치 전략
- `main` → Railway 자동 배포 (push 즉시)
- `gh-pages` → Flutter 웹 정적 파일만 (빌드 결과물)
- feature 브랜치 → PR → main 머지 (팀원 작업)

### 팀원 PR 머지 시 주의
팀원 브랜치 기준점이 Phase 2-3 이전일 경우 아래 파일이 롤백되는 패턴 반복됨:
- `server/app/api/v1/preorders.py`
- `server/app/services/preorder_service.py`
- `server/app/db/repositories/preorder_repository.py`
- `server/tests/test_preorders.py`

머지 전 반드시 `git diff main..feature-branch -- server/app/api/v1/preorders.py` 확인.  
충돌 시 `git checkout main -- <파일>` 로 복원 후 재커밋.

### KAMIS 품목코드 매핑
`price_service.py`의 `KAMIS_ITEM_MAP` — MVP 기준 7개 품목만 지원:
`112`(배추), `214`(사과), `215`(배), `421`(감), `151`(무), `152`(당근), `111`(쌀)

### 장보기 에이전트 레시피 데이터셋
`shopping_agent_service.py`의 `_RECIPE_DATASET` — 현재 3개 레시피 하드코딩:
- 고추장찌개 (키워드: 찌개, 저녁)
- 봄나물 비빔밥 (키워드: 비빔밥, 채소)
- 볶음밥 (키워드: 볶음밥, 점심)

### gh-pages 배포 주의
- `--base-href "/market-mvp/"` 필수 (GitHub Pages 서브경로)
- `.nojekyll` 파일 루트에 유지 필요
- `.env`, `server/`, `client/` 등 소스 파일이 gh-pages에 혼입되지 않도록 주의
