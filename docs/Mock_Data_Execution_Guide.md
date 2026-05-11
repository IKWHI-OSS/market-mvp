# Mock Data 실행 가이드 (시연용)

## 1) 목적
- 시연 안정성을 위해 기능별 모킹데이터를 분리해 관리한다.
- 기본 데이터(`data/mock`)는 공통으로 유지하고, 시나리오별 확장 데이터만 프로필로 병합한다.

## 2) DB를 모를 때 꼭 알아야 할 최소 개념
- `schema.sql`: 테이블 구조 정의서 (틀)
- `seed`: 테이블에 넣는 샘플 데이터
- `profile`: 시연 시나리오별 추가 데이터 묶음
- 지금 구조는 **기본 데이터 + 프로필 데이터(추가분)** 방식이다.

## 3) 현재 구성
- 기본 데이터: `data/mock/*.json`
- 프로필 데이터: `data/mock/profiles/<profile>/*.json`
- 시드 스크립트: `scripts/seed_mock.py`

사용 가능한 프로필:
- `consumer_demo`: 소비자 장보기/알림/이벤트 중심
- `merchant_demo`: 상인 신규 점포/상품/드랍 중심
- `agent_demo`: 장보기 에이전트 재료-점포 매칭 강화 중심

## 4) 실행 방법 (로컬 MySQL)
사전조건:
- MySQL 실행 중
- `.env`에 DB 접속 정보 존재 (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`)

### 4.1 공통(기본) 데이터만 시딩
```bash
cd /Users/ifxxkingblueyou/제조AI_부트캠프/프로젝트_서울시공공데이터창업/project/market-mvp
python3 scripts/seed_mock.py
```

### 4.2 프로필 병합 시딩
```bash
# 소비자 시연
python3 scripts/seed_mock.py --profile consumer_demo

# 상인 시연
python3 scripts/seed_mock.py --profile merchant_demo

# 장보기 에이전트 시연
python3 scripts/seed_mock.py --profile agent_demo
```

## 5) 시연 운영 권장 순서
1. `consumer_demo` 시딩 → 홈/드랍/리스트/알림 확인
2. `merchant_demo` 시딩 → 상인 스토리/상품/드랍 확인
3. `agent_demo` 시딩 → 장보기 에이전트 질의 후 매칭 확인

## 6) 팀원 분담 가이드
- 팀원 A(소비자): `consumer_demo` JSON만 관리
- 팀원 B(상인): `merchant_demo` JSON만 관리
- 팀원 C(에이전트): `agent_demo` JSON만 관리

규칙:
- 기존 파일 수정 최소화, 신규 ID로 추가
- `*_id`는 중복 금지
- 날짜/상태값은 기획 문서 정책 준수

## 7) 체크리스트 (시연 전)
- [ ] 로그인 계정 확인 (`consumer01`, `merchant01`, `merchant03`)
- [ ] 드랍 이벤트 상태(`scheduled/arrived/sold_out`) 확인
- [ ] 장보기 에이전트 질의: "2인 저녁 찌개 재료 추천"
- [ ] 상인 스토리 생성 API 정상 확인
- [ ] 프론트 문구가 "AI 실패"와 "매칭 데이터 부족"을 구분하는지 확인

## 8) Railway 반영 시 주의
- Railway는 DB 재배포/재기동 시 데이터가 초기화될 수 있다.
- 따라서 시연 직전 아래 2가지를 고정한다:
  1. 어떤 프로필을 넣을지 (`consumer_demo`/`merchant_demo`/`agent_demo`)
  2. 시딩 실행 로그를 캡처해 공유
