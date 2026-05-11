# 📦 프론트 연동 자료 핸드오프 (2026-05-11)

안녕하세요!  
요청해주신 API 계약서 최종본 + 부속 자료 전부 준비 완료해서 main 브랜치에 푸시했습니다. 커밋은 `cde96bb` 이에요. Railway 자동 배포돼서 1분이면 반영됩니다.

확인하실 순서는 아래대로 따라가시면 됩니다 👇

---

## 1️⃣ 우선 이 4개만 보시면 됩니다 — 깃 기준 위치

리포: `https://github.com/IKWHI-OSS/market-mvp` (main 브랜치)

| 파일 | 어디서 | 무엇을 보면 되는지 |
|---|---|---|
| 📄 **API 계약서** | `docs/API_Specification.md` | **이게 메인입니다.** v2.0, 전체 37개 엔드포인트의 요청/응답·권한·에러 코드·페이지네이션 규약 다 들어있어요. 위에서부터 차례로 읽으시면 됩니다. |
| 🧪 **Postman 컬렉션** | `docs/postman_collection.json` | Postman에서 Import → JSON 선택 → 이 파일 올리면 36개 요청 다 들어옵니다. 첫 화면에서 `Login` 한 번 누르면 토큰 자동 저장돼서 다른 요청 그대로 쏠 수 있어요. |
| 🆔 **샘플 ID 모음** | `docs/sample_ids.md` | 화면별로 어떤 `store_id`, `product_id`, `story_id` 쓰면 좋은지 표로 정리. 시드 데이터가 500여 개라 다 보기 부담스러우니까 여기서 골라 쓰시면 됩니다. |
| 🌐 **Swagger UI (실시간)** | https://market-api-production-6e52.up.railway.app/docs | FastAPI 자동 문서. 브라우저에서 바로 "Try it out" 가능해요. |

> ⚠️ 옛날 v1.2 문서 보지 마세요. v2.0이 진짜 최종본입니다.

---

## 2️⃣ 핵심 변경점 (요청해주신 항목 기준)

### 신규 엔드포인트 — 6개 아니라 **12개**예요
- 스토리 7개: `POST/GET/PATCH/PATCH publish/DELETE merchant/stories` + `GET stores/{id}/story`
- 가격 5개: `GET/POST prices/market/{code}`, `POST merchant/products/{id}/price`, `GET .../price-history`, `GET merchant/dashboard/price-suggestions`
- (참고로 Preorder API 5개, Shopping Agent 1개도 같이 살아있어요)

### 스토리 POST 응답
- `story_id` ✅ 항상 옵니다 (persist=false 일 때만 null)
- `is_published` ✅ 항상 옵니다
- `published_at` ✅ **요청하신 대로 응답에 추가했어요** — publish=false면 null

### PATCH publish 응답
- **업데이트된 전체 객체** 반환합니다 (최소 필드 아님). 화면에서 그대로 갈아끼우시면 돼요.

### Soft delete 제외 기준
- `deleted_at IS NULL` 필터가 모든 조회에 자동 적용됩니다. 삭제하면 목록·단건 조회 다 안 보여요. 추가로 삭제 시 `is_published`도 자동 0으로 떨어집니다.

### 점포별 기본 정렬
- `GET /merchant/stories`: **게시 우선 → 최신순** (`is_published DESC, created_at DESC`)
- 페이지네이션 적용했습니다 (`page`, `size` 쿼리).

### price-history 응답
- 필드: `history_id, old_price, new_price, change_amount, change_rate, reason, reference_id, created_at`
- 정렬: **최신순** (`created_at.desc()`)
- 날짜: ISO-8601 UTC. 프론트에서 KST 변환해주세요.

### KAMIS 매핑 규칙
- `price_service.py` 안에 `PRODUCT_KAMIS_KEYWORDS` 사전(2자 이상 키워드) 우선 매칭 → 폴백으로 `KAMIS_ITEM_MAP.item_name` 접두 매칭. 30품목 지원합니다.

### diff_pct 계산식
- `(현재가 - KAMIS 소매가) / KAMIS 소매가 × 100`, 소수 1자리
- 임계값 `±10%` 기준 3분기 권장 문구 자동 생성 (계약서 7.5절에 상세)

### 권한 정책
- 소비자가 `GET /stores/{id}/story` 비공개·미게시 점포 호출 → **200 OK + `data: {}`** (404 아님)
- 상인이 다른 점포 자원 건드릴 때 → **403 FORBIDDEN**
- 가격 업데이트/이력 조회도 본인 점포 검증 추가했습니다 (이전엔 product_id만으로 권한 통과돼서 보강)

---

## 3️⃣ 테스트 환경

### 계정 (전부 비밀번호 `password123`)
- 소비자: `consumer01@market.com` ~ `consumer04@market.com`
- 상인: `merchant01@market.com`, `merchant02@market.com`

### Railway 시드 현황
- User 50, Market 11, Store 101, Product 497
- Story 207건(전부 게시), MarketPrice 900건, PriceHistory 303건, Drop 120건

### fallback 모드 확인 방법
- 응답 JSON에서 `fallback_mode: true` 만 보시면 됩니다.
- 강제로 보고 싶으시면 백엔드한테 Railway 환경변수에서 `ANTHROPIC_API_KEY` / `KAMIS_API_KEY` 잠깐 빼달라고 하시면 돼요.

---

## 4️⃣ 변경 정책

- **optional 필드 추가**는 언제든 해도 됩니다 (프론트 깨질 일 없음).
- **필드 삭제/이름 변경/타입 변경**은 v2 만들어서 합니다. v1 응답은 안 깹니다.
- 이번 v2.0이 **최종 계약서**예요. 이후 breaking change 없습니다.

---

## 5️⃣ 막힐 때

문서에서 안 풀리는 부분 있으면 다음 순서로 확인해보세요:

1. `docs/API_Specification.md` 해당 섹션 다시 읽기
2. Swagger UI (`https://market-api-production-6e52.up.railway.app/docs`) 에서 직접 Try it out
3. Postman 컬렉션에서 같은 요청 쏴보기 (인증 토큰 자동 처리됨)
4. 그래도 안 풀리면 백엔드 핑 주세요

---

작업하시다 응답 필드가 문서랑 다른 부분 보이면 바로 알려주세요. 코드와 문서를 다시 맞추겠습니다 🙌
