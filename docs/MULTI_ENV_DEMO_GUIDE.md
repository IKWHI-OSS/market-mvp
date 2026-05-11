# 단일 웹에서 분리된 환경으로 시연하기 — 프론트 작업자 가이드

> 대상: **프론트 작업자**  
> 목적: 백엔드/프론트 각자 자기 Railway DB·API 키·모킹데이터를 **그대로 유지**하면서, **하나의 Flutter 웹 화면에서 토글 한 번으로 양쪽 데이터 시연**.  
> 작성: 백엔드 작업자, 2026-05-11

---

## 0) 결론부터 — 왜 "각자 따로"가 더 깔끔한가 (꼭 읽어주세요)

이 가이드의 전제는 **DB와 .env를 통합하지 않고 분리한 채로 유지**하는 거예요. 결정 근거를 명시해둡니다:

### ✅ 분리 유지가 깔끔한 이유 (4가지)

1. **데이터 충돌 0** — 모킹데이터는 각자가 시뮬레이션 시나리오에 맞게 만든 거라 합치면 ID·시드 규모·테스트 시나리오가 서로를 깨뜨립니다. 핸드오프 문서 11장 "모킹데이터 충돌 방지 규칙"이 이미 분리 전제로 작성돼 있어요. 이 규칙을 살리려면 **분리 유지가 디폴트**가 맞습니다.

2. **API 키 비용·사용량 추적이 명확** — Anthropic 키가 각자 것이라 호출량·과금이 본인에게만 잡힙니다. 통합하면 누가 얼마나 썼는지 분리 불가능해지고, 키 노출 시 폭발 범위도 커져요.

3. **백엔드 코드 변경이 0** — 통합 방식(헤더 기반 DB 라우팅 등)은 `server/app/db/session.py`·`Depends(get_db)` 손봐야 하고 테스트도 다 다시 돌려야 합니다. **분리 + 클라이언트 토글은 백엔드 한 줄도 안 바뀝니다.**

4. **시연에서 학습 포인트 살아남** — "각자 분리된 환경, 같은 UI 코드, 토글로 데이터만 갈아끼움"이 그대로 발표 포인트가 됩니다. 통합하면 "그냥 합쳐서 한 DB 썼습니다"가 되어 아키텍처 의사결정 흔적이 사라져요. 학습 프로젝트의 핵심은 **분리/통합 트레이드오프를 의식적으로 선택한 흔적**이고, 그 흔적이 토글 코드 한 군데에 남는 게 가장 깔끔합니다.

### ❌ 통합하면 생기는 문제 (구체적)

- 한쪽 모킹데이터를 다른 쪽이 덮어쓸 위험 (시드 스크립트 충돌)
- 한 사람이 DB 스키마 migration 한 번 잘못 누르면 양쪽 다 박살
- Anthropic 키 통합 → 한쪽이 quota 초과하면 다른 쪽 기능도 같이 죽음
- 핸드오프 문서 11장 "DB 분리·ID 네임스페이스 규칙"을 다시 써야 함
- git에서 `server/.env`를 누가 마지막에 푸시했냐에 따라 상대 환경이 깨짐

→ **분리 + 토글이 명확히 우월합니다.** 이 가이드는 그 전제로 작성됐어요.

---

## 1) 구조 한 장 요약

```
┌─────────────────────────────────────────────────┐
│  Flutter Web — 단일 코드베이스                   │
│  ┌─────────────────────────────────────────┐    │
│  │ 화면 어디서든 [환경 토글] 버튼           │    │
│  │  ◉ 백엔드 작업자 환경                    │    │
│  │  ○ 프론트 작업자 환경                    │    │
│  └─────────────────────────────────────────┘    │
│             ↓ ApiClient.baseUrl 동적 전환        │
└──────────┬──────────────────┬───────────────────┘
           ↓                  ↓
   Railway A (백엔드 작업자)   Railway B (프론트 작업자)
   ├─ DB_A (백엔드 작업자 모킹) ├─ DB_B (프론트 작업자 모킹)
   ├─ ANTHROPIC_KEY_A          ├─ ANTHROPIC_KEY_B
   └─ 시드 my_demo 프로필      └─ 시드 your_demo 프로필
```

- 백엔드 코드, DB, .env, API 키, 모킹데이터: **양쪽 모두 그대로 유지**
- 변경되는 곳: **프론트 코드 1~2개 파일만**
- 사용자(시연자) 경험: 한 웹사이트, 토글 한 번으로 양쪽 데이터 보기

---

## 2) 백엔드 작업자 측 상태 (참고용 — 따로 할 일 없음)

이미 완료된 부분이니 프론트 작업자가 의식할 필요는 없지만, 디버깅에 도움 되라고 적어둡니다:

| 항목 | 상태 |
|---|---|
| Railway 백엔드 URL | `https://market-api-production-6e52.up.railway.app` |
| CORS 설정 | `allow_origins=["*"]` 적용됨 (어느 도메인에서든 호출 가능) |
| OpenAPI 문서 | `https://market-api-production-6e52.up.railway.app/docs` |
| API 계약서 | `docs/API_Specification.md` v2.0 (이미 main에 머지됨) |
| Anthropic 키 | 백엔드 작업자 본인 키 사용 중, 분리 유지 |
| 모킹 시드 | mock_v2 프로필 (users 50/stores 101/products 497/stories 207 등) |

→ **백엔드는 한 줄도 바꿀 필요 없습니다.** 프론트 측 작업만 끝나면 시연 가능.

---

## 3) 프론트 작업자 체크리스트 (이 부분만 하시면 됩니다)

### 사전 준비
- [ ] **본인의 Railway 백엔드가 떠있는지 확인**. 없으면 본인 fork/branch에서 Railway 한 번 배포해두세요.
  - 본인 Railway URL을 기록해두세요. 예: `https://market-api-yours.up.railway.app/api/v1`
- [ ] 본인 Railway에 본인 모킹 데이터 시드 완료 상태인지 확인 (`/health` + `/api/v1/products/search?q=시금치` 응답 OK)
- [ ] 백엔드 작업자 Railway도 응답하는지 한 번 ping (`curl https://market-api-production-6e52.up.railway.app/health`)

### 작업 1: 환경 enum 신규 파일 추가
`client/lib/core/network/api_environment.dart` 신규 생성:

```dart
enum ApiEnvironment {
  backend(
    label: '백엔드 작업자 환경',
    baseUrl: String.fromEnvironment(
      'API_BASE_BACKEND',
      defaultValue: 'https://market-api-production-6e52.up.railway.app/api/v1',
    ),
    tokenKey: 'access_token_backend',
  ),
  frontend(
    label: '프론트 작업자 환경',
    baseUrl: String.fromEnvironment(
      'API_BASE_FRONTEND',
      defaultValue: 'https://market-api-yours.up.railway.app/api/v1', // ← 본인 Railway URL로 교체
    ),
    tokenKey: 'access_token_frontend',
  );

  const ApiEnvironment({
    required this.label,
    required this.baseUrl,
    required this.tokenKey,
  });

  final String label;
  final String baseUrl;
  final String tokenKey;
}
```

> 💡 `defaultValue` 두 곳을 본인 환경에 맞게 수정. `--dart-define`을 줄 거면 defaultValue는 비워두셔도 됩니다.

### 작업 2: `api_client.dart` 수정

**현재 상태** (`client/lib/core/network/api_client.dart` 4번째 줄 근처):
```dart
const _baseUrl = 'https://market-api-production-6e52.up.railway.app/api/v1';
```

**변경 후**:
```dart
import 'api_environment.dart';
import 'package:shared_preferences/shared_preferences.dart'; // 이미 있다면 생략

class ApiClient {
  static final ApiClient instance = ApiClient._();
  ApiClient._();

  ApiEnvironment _env = ApiEnvironment.backend;  // 디폴트는 백엔드 환경
  String? _token;

  ApiEnvironment get env => _env;
  String get baseUrl => _env.baseUrl;
  String? get token => _token;

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    final savedEnvName = prefs.getString('current_env') ?? ApiEnvironment.backend.name;
    _env = ApiEnvironment.values.firstWhere(
      (e) => e.name == savedEnvName,
      orElse: () => ApiEnvironment.backend,
    );
    _token = prefs.getString(_env.tokenKey);
  }

  Future<void> setEnvironment(ApiEnvironment newEnv) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('current_env', newEnv.name);
    _env = newEnv;
    _token = prefs.getString(newEnv.tokenKey);  // 환경별 토큰 로드
  }

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_env.tokenKey, token);
    _token = token;
  }

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_env.tokenKey);
    _token = null;
  }
}
```

→ 기존 모든 HTTP 호출은 `_baseUrl` 대신 `ApiClient.instance.baseUrl` 사용하도록 일괄 치환.  
→ 토큰 저장도 기존 `setString('access_token', ...)` 대신 `ApiClient.instance.saveToken(...)`.

### 작업 3: 토글 위젯 추가
시연 편의용. **마이페이지 / 디버그 메뉴 / 앱바 모서리** 어디든:

```dart
PopupMenuButton<ApiEnvironment>(
  icon: const Icon(Icons.swap_horiz),
  tooltip: '환경 전환',
  initialValue: ApiClient.instance.env,
  onSelected: (newEnv) async {
    await ApiClient.instance.setEnvironment(newEnv);
    if (!context.mounted) return;
    // 로그인 토큰이 환경별로 분리돼 있어 재로그인 필요할 수 있음
    Navigator.pushNamedAndRemoveUntil(context, '/', (_) => false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${newEnv.label}으로 전환됨')),
    );
  },
  itemBuilder: (_) => ApiEnvironment.values.map((e) {
    return PopupMenuItem(
      value: e,
      child: Row(
        children: [
          Icon(
            ApiClient.instance.env == e ? Icons.radio_button_checked : Icons.radio_button_off,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(e.label),
        ],
      ),
    );
  }).toList(),
)
```

### 작업 4: `main.dart`에서 초기화
앱 시작 시 환경 정보 로드:
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ApiClient.instance.initialize();
  runApp(const MyApp());
}
```

### 작업 5: 실행 명령어
```bash
flutter run -d web-server --web-port 5179 \
  --dart-define=API_BASE_BACKEND=https://market-api-production-6e52.up.railway.app/api/v1 \
  --dart-define=API_BASE_FRONTEND=https://market-api-yours.up.railway.app/api/v1
```

`--dart-define` 안 줘도 코드의 `defaultValue`가 적용되니까 본인 편한 방식으로.

---

## 4) Git 충돌 안 나는 작업 분담

### 파일 경로별 소유권 (이미 자연스럽게 분리됨)

| 영역 | 담당 | 변경 가능 경로 |
|---|---|---|
| 백엔드 작업자 | 본인 | `server/**`, `scripts/**`, `data/**`, `docs/**`, `db/**` |
| 프론트 작업자 | **귀하** | `client/**` 전부 |

→ **이번 작업에서 양쪽이 건드리는 파일이 0** (백엔드 작업자는 docs/만 추가, 프론트 작업자는 client/만 수정).

### 권장 Git 흐름

**프론트 작업자 (귀하)**:
```bash
git pull origin main                              # 이 가이드 문서를 받아옴
git checkout -b feat/multi-env-toggle             # 본인 작업 브랜치
# … client/ 안에서만 작업 (위 작업 1~5) …
git add client/                                   # client/ 만 add
git commit -m "feat: 멀티 환경 토글 추가 — 백엔드/프론트 환경 분리 유지"
git push origin feat/multi-env-toggle             # 본인 브랜치만 푸시
# GitHub에서 PR 생성 → main으로 머지
```

**백엔드 작업자 (이미 끝남)**:
- 이 가이드 문서(`docs/MULTI_ENV_DEMO_GUIDE.md`)만 main에 푸시됨
- `server/`나 `client/` 손 안 댐 → 충돌 0

### 충돌 0 보장 근거
- `client/lib/core/network/api_environment.dart` — **신규 파일** (어디서도 충돌 불가)
- `client/lib/core/network/api_client.dart` — 프론트 작업자 단독 영역 (백엔드 작업자는 손 안 댐)
- `client/lib/main.dart`, 토글 위젯 — 마찬가지로 프론트 단독 영역
- `docs/MULTI_ENV_DEMO_GUIDE.md` — 백엔드 작업자가 추가, 프론트는 읽기만

→ **양쪽이 동시에 push해도 git 충돌 0**.

---

## 5) 시연 검증 체크리스트

작업 끝나면 아래 순서로 검증해주세요:

### 5.1 환경 토글 동작
- [ ] 앱 켜면 디폴트로 백엔드 작업자 환경 진입
- [ ] 우상단(또는 마이페이지) 토글 누르면 환경 선택 팝업 나옴
- [ ] 프론트 작업자 환경 선택 → 메인 화면 새로고침됨
- [ ] 다시 켜도 마지막 선택 환경 유지 (SharedPreferences 저장)

### 5.2 데이터 분리 확인
- [ ] 백엔드 작업자 환경에서 `consumer01@market.com` / `password123` 로그인 OK
- [ ] 홈 화면에 백엔드 작업자 시드 데이터(망원시장·시금치 등) 표시
- [ ] 환경 토글 → 프론트 작업자 환경 → 본인 시드 데이터 표시 (다른 시장·상품)
- [ ] 토글 후 다시 로그인 필요한지 확인 (토큰 분리 정상 동작)

### 5.3 핵심 기능 양쪽 환경에서 모두 동작
- [ ] 홈 화면 (드랍/이벤트/스포트라이트)
- [ ] 검색 (`q=시금치` 등)
- [ ] 드랍 리스트
- [ ] 장보기 에이전트 (Anthropic 호출 — 각 환경의 API 키로 호출되는지 확인)
- [ ] 상인 스토리 생성 (`merchant01@market.com` 로그인 후)
- [ ] 가격 이력 화면

### 5.4 fallback 모드 검증 (선택)
- [ ] 한쪽 Railway에서 Anthropic 키 임시 제거 → 스토리 생성 시 `fallback_mode: true` 응답
- [ ] 토글로 다른 환경 가면 정상 LLM 응답

---

## 6) 시연 시나리오 (발표용 추천 흐름)

1. "각자 분리된 환경, 동일한 코드" 슬라이드
2. 앱 켜기 → 디폴트 환경(백엔드 작업자) 데이터로 홈 화면 보여줌
3. 우상단 토글 클릭 → "프론트 작업자 환경" 선택
4. 같은 화면, **다른 데이터** (다른 시장·상품·스토리) 표시되는 모습 보여줌
5. "백엔드 코드 한 줄도 안 바꿨다" + "프론트 토글 코드 한 군데만 추가" 강조
6. 의사결정 흔적: "분리 vs 통합 트레이드오프를 의식적으로 선택" — 학습 포인트로 마무리

---

## 7) 자주 묻는 질문

**Q. 토글했는데 데이터가 안 바뀌어요.**  
A. 브라우저 캐시. `Cmd+Shift+R` 강제 새로고침. 또는 `setEnvironment` 후 `Navigator.pushNamedAndRemoveUntil`로 트리 재구성하는지 확인.

**Q. CORS 에러 떠요.**  
A. 백엔드 양쪽 모두 `allow_origins=["*"]` 확인. 본인 Railway에 배포된 `server/app/main.py`도 같은 설정인지 확인하세요.

**Q. 토큰이 섞여요.**  
A. `tokenKey`가 환경별로 다른지 확인 (`access_token_backend` vs `access_token_frontend`). 같으면 한쪽 로그인이 다른쪽으로 새요.

**Q. 본인 Railway가 없는데요?**  
A. 본인 fork에서 Railway 한 번 배포(5분). `server/.env`에 본인 DB URL·Anthropic 키 세팅 후 `git push` → Railway 자동 배포. 그 URL을 `api_environment.dart`에 박아주세요.

**Q. 시연 환경에서 자꾸 백엔드 작업자 키로만 Anthropic 호출되는데요?**  
A. 정상입니다. 백엔드 환경을 선택하면 백엔드 Railway가 받고 → 백엔드의 .env에 있는 Anthropic 키로 호출. 프론트 환경 선택하면 프론트 Railway → 프론트 키. **이게 분리의 핵심**.

---

## 8) 마무리

**한 줄 요약**: `client/lib/core/network/` 안에서 enum 1개 + ApiClient 토큰 분리만 손보면 끝. 백엔드는 0줄. 충돌도 0. 분리도 0% 깨지지 않고 유지.

작업하다 막히면 백엔드 작업자한테 핑 주세요. 이 가이드 따라가다 명확하지 않은 부분 발견하면 그것부터 잡아드릴게요. 화이팅 🚀
