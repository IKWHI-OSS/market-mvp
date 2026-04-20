"""
market_collect.py — 서울 열린데이터광장 전통시장 현황 API에서
망원시장·통인시장 데이터를 수집해 data/real/markets.json으로 저장합니다.

API: 서울 열린데이터광장 전통시장 현황
  http://openapi.seoul.go.kr:8088/{API_KEY}/json/ListTraditionalMarket/1/1000/

환경변수(.env):
  SEOUL_API_KEY  — 서울 열린데이터광장 인증키
                   https://data.seoul.go.kr 에서 발급

fallback:
  API 호출 실패 시 망원시장·통인시장 하드코딩 데이터를 사용합니다.
"""

import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# 환경변수 로드 (.env 파일 지원 — python-dotenv 없이 직접 파싱)
# ---------------------------------------------------------------------------

def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv()

SEOUL_API_KEY = os.getenv("SEOUL_API_KEY", "")
SEOUL_API_BASE = "http://openapi.seoul.go.kr:8088"
SERVICE_NAME = "ListTraditionalMarket"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "real"
OUTPUT_FILE = OUTPUT_DIR / "markets.json"

# 수집 대상 시장명
TARGET_MARKETS = {"망원시장", "통인시장"}

# ---------------------------------------------------------------------------
# Fallback 데이터 (API 실패 시 사용)
# ---------------------------------------------------------------------------

FALLBACK_MARKETS: list[dict] = [
    {
        "market_name": "망원시장",
        "address": "서울특별시 마포구 망원로8길 일대 망원시장",
        "lat": 37.5556,
        "lng": 126.9104,
    },
    {
        "market_name": "통인시장",
        "address": "서울 종로구 자하문로15길 18 통인시장",
        "lat": 37.5796,
        "lng": 126.9688,
    },
]

# ---------------------------------------------------------------------------
# API 호출
# ---------------------------------------------------------------------------

def _build_url(start: int = 1, end: int = 1000) -> str:
    return f"{SEOUL_API_BASE}/{SEOUL_API_KEY}/json/{SERVICE_NAME}/{start}/{end}/"


def fetch_from_api() -> list[dict]:
    """서울 열린데이터광장에서 전통시장 목록을 가져와 대상 시장만 필터링합니다."""
    if not SEOUL_API_KEY:
        raise ValueError("SEOUL_API_KEY not set")

    url = _build_url()
    print(f"[API] GET {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})

    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    service = raw.get(SERVICE_NAME, {})
    result_code = service.get("RESULT", {}).get("CODE", "")
    if not result_code.startswith("INFO-000"):
        raise RuntimeError(f"API error: {service.get('RESULT')}")

    rows = service.get("row", [])
    print(f"[API] 총 {len(rows)}개 시장 조회됨")

    found: list[dict] = []
    for row in rows:
        # 실제 API 필드명: ITEM_NM
        name = row.get("ITEM_NM", "").strip()
        if name not in TARGET_MARKETS:
            continue

        def _float(val, default=None):
            try:
                f = float(val or 0)
                return f if f != 0.0 else default
            except (TypeError, ValueError):
                return default

        found.append({
            "market_name": name,
            "address": row.get("ITEM_ADDR") or "",
            "lat": _float(row.get("LATITUDE")),
            "lng": _float(row.get("LONGITUDE")),
        })

    return found


# ---------------------------------------------------------------------------
# Fallback 병합
# ---------------------------------------------------------------------------

def _apply_fallback(collected: list[dict]) -> list[dict]:
    """수집된 데이터 중 위경도 누락 항목을 fallback으로 보완합니다."""
    fallback_map = {m["market_name"]: m for m in FALLBACK_MARKETS}
    result = []
    for item in collected:
        fb = fallback_map.get(item["market_name"], {})
        result.append({
            "market_name": item["market_name"],
            "address": item["address"] or fb.get("address", ""),
            "lat": item["lat"] if item["lat"] is not None else fb.get("lat"),
            "lng": item["lng"] if item["lng"] is not None else fb.get("lng"),
        })
    return result


def _ensure_all_targets(collected: list[dict]) -> list[dict]:
    """수집 결과에 누락된 대상 시장을 fallback으로 추가합니다."""
    found_names = {m["market_name"] for m in collected}
    result = list(collected)
    for fb in FALLBACK_MARKETS:
        if fb["market_name"] not in found_names:
            print(f"[FALLBACK] '{fb['market_name']}' — API 미수집, fallback 사용")
            result.append(fb)
    return result


# ---------------------------------------------------------------------------
# UUID 부여 및 저장
# ---------------------------------------------------------------------------

def save(markets: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 기존 파일이 있으면 market_id 재사용 (market_name 기준)
    existing: dict[str, str] = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for item in json.load(f):
                existing[item["market_name"]] = item["market_id"]

    result = []
    for m in markets:
        mid = existing.get(m["market_name"], str(uuid.uuid4()))
        result.append({"market_id": mid, **{k: v for k, v in m.items() if k != "market_id"}})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[SAVED] {OUTPUT_FILE}  ({len(result)}개 시장)")
    for m in result:
        print(f"  • {m['market_name']}  lat={m['lat']}  lng={m['lng']}")


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main() -> None:
    collected: list[dict] = []

    if SEOUL_API_KEY:
        try:
            collected = fetch_from_api()
            collected = _apply_fallback(collected)
            print(f"[API] 대상 시장 {len(collected)}개 수집 완료")
        except Exception as exc:
            print(f"[WARN] API 호출 실패 → fallback 사용  ({exc})")
            collected = []
    else:
        print("[WARN] SEOUL_API_KEY 미설정 → fallback 데이터 사용")

    collected = _ensure_all_targets(collected)
    save(collected)


if __name__ == "__main__":
    main()
