"""
kamis_collect.py — KAMIS(농산물유통정보) API에서 가격 데이터를 수집합니다.
수집 결과는 data/real/kamis_prices_YYYYMMDD.json 으로 저장됩니다.

KAMIS API 문서: https://www.kamis.or.kr/customer/reference/openApi_list.do
환경변수:
  KAMIS_API_KEY  — KAMIS 발급 인증키
  KAMIS_CERT_ID  — KAMIS 인증 ID
"""

import os
import json
import datetime
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

KAMIS_API_KEY = os.getenv("KAMIS_API_KEY", "")
KAMIS_CERT_ID = os.getenv("KAMIS_CERT_ID", "")
BASE_URL = "https://www.kamis.or.kr/service/price/xml.do"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "real")

# KAMIS 품목 코드 및 이름
ITEMS = [
    {"code": "111", "kind": "01", "name": "쌀"},
    {"code": "214", "kind": "01", "name": "배추"},
    {"code": "215", "kind": "01", "name": "무"},
    {"code": "216", "kind": "01", "name": "양파"},
    {"code": "217", "kind": "01", "name": "마늘"},
    {"code": "232", "kind": "01", "name": "대파"},
    {"code": "244", "kind": "01", "name": "고추"},
    {"code": "412", "kind": "01", "name": "사과"},
    {"code": "413", "kind": "01", "name": "배"},
    {"code": "514", "kind": "01", "name": "돼지고기"},
    {"code": "515", "kind": "01", "name": "쇠고기"},
]


def fetch_price(item: dict) -> dict:
    today = datetime.date.today().strftime("%Y-%m-%d")
    params = {
        "action": "dailySalesList",
        "p_cert_key": KAMIS_API_KEY,
        "p_cert_id": KAMIS_CERT_ID,
        "p_returntype": "json",
        "p_productclscode": "02",       # 02: 소매
        "p_startday": today,
        "p_endday": today,
        "p_itemcode": item["code"],
        "p_kindcode": item["kind"],
        "p_productrankcode": "04",      # 04: 상품
        "p_countrycode": "1101",        # 1101: 서울
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def collect() -> list[dict]:
    results = []
    for item in ITEMS:
        try:
            data = fetch_price(item)
            prices = data.get("price", [])
            results.append({
                "item_code": item["code"],
                "item_name": item["name"],
                "data": prices,
            })
            print(f"[OK] {item['name']} ({item['code']}) — {len(prices)}건")
        except Exception as e:
            print(f"[ERROR] {item['name']} ({item['code']}): {e}")
    return results


def save(results: list[dict]):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"kamis_prices_{datetime.date.today().strftime('%Y%m%d')}.json"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVED] {path}  ({len(results)}개 품목)")


def main():
    if not KAMIS_API_KEY:
        print("[WARN] KAMIS_API_KEY not set — .env 파일을 확인하세요")
        return
    print(f"[START] KAMIS 가격 데이터 수집 ({datetime.date.today()})\n")
    results = collect()
    save(results)


if __name__ == "__main__":
    main()
