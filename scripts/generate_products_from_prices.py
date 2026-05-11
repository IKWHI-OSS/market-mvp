"""
generate_products_from_prices.py
서울시 주요품목가격 수집 결과(data/real/seoul_prices_YYYYMMDD.json)를 이용해
agent_demo용 Product 모킹데이터를 대량 생성한다.

출력:
  data/mock/profiles/agent_demo/products.json (기존 데이터 + 신규 merge)

사용 예:
  python3 scripts/generate_products_from_prices.py --target-count 180
"""

from __future__ import annotations

import argparse
import json
import random
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).parent.parent
REAL_DIR = ROOT / "data" / "real"
STORE_FILE = ROOT / "data" / "mock" / "stores.json"
OUT_FILE = ROOT / "data" / "mock" / "profiles" / "agent_demo" / "products.json"


def _latest_price_file() -> Path:
    files = sorted(REAL_DIR.glob("seoul_prices_*.json"))
    if not files:
        raise FileNotFoundError("seoul_prices_*.json 파일이 없습니다. 먼저 seoul_price_collect.py를 실행하세요.")
    return files[-1]


def _parse_price(value: str) -> int | None:
    if not value:
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return None
    n = int(digits)
    if n <= 0:
        return None
    return n


def _parse_unit_qty(unit_qty: str) -> int | None:
    if not unit_qty:
        return None
    m = re.search(r"\d+", str(unit_qty))
    if not m:
        return None
    n = int(m.group(0))
    return n if n > 0 else None


def _normalize_item_name(name: str) -> str:
    s = name.strip()
    # API 데이터에 붙는 접미어 정리
    for suffix in ("(상품)", "(중품)", "(상품)"):
        s = s.replace(suffix, "")
    return s.strip()


def _retail_unit_for(item_name: str) -> tuple[str, int]:
    """
    반환: (표시 단위, 도매단위 기준 환산 배수)
    - 환산 배수는 입력 raw_price를 소매 단위로 변환할 때 사용
      ex) 10kg 박스 가격 -> 1kg 가격이면 multiplier=1
    """
    n = item_name
    # 1kg 기준 품목
    per_kg_keywords = [
        "고구마", "감자", "양파", "무", "배추", "당근", "오이", "호박",
        "사과", "배", "귤", "감귤", "포도", "토마토",
    ]
    if any(k in n for k in per_kg_keywords):
        return ("1kg", 1)

    # 개당 기준 품목
    per_each_keywords = ["수박", "참외", "파인애플", "망고", "복숭아", "배추포기"]
    if any(k in n for k in per_each_keywords):
        return ("1개", 1)

    # 단/봉 기준 품목
    if any(k in n for k in ["대파", "쪽파", "부추", "미나리"]):
        return ("1단", 1)
    if any(k in n for k in ["시금치", "상추", "깻잎", "쑥갓", "콩나물", "숙주"]):
        return ("1봉", 1)
    return ("1팩", 1)


def _retail_price(src: dict) -> tuple[int, str]:
    raw_price = _parse_price(src.get("price_raw", ""))
    if raw_price is None:
        return random.randint(1500, 15000), "1팩"

    item_name = _normalize_item_name(str(src.get("item_name", "")))
    unit_qty = _parse_unit_qty(str(src.get("raw", {}).get("UNIT_QTY", "")))
    unit_name = str(src.get("unit", "") or src.get("raw", {}).get("U_NAME", ""))

    display_unit, multiplier = _retail_unit_for(item_name)

    # 기본은 원본가 유지
    base = raw_price
    if unit_qty and unit_qty > 1:
        # 10키로상자 -> 1kg 단가 같은 형태로 환산
        if "키로" in unit_name or "kg" in unit_name.lower():
            base = raw_price / unit_qty
        elif "개" in unit_name or "입" in unit_name:
            base = raw_price / unit_qty
        # 단/봉은 UNIT_QTY가 의미 없을 수 있어 그대로 유지

    retail = int(round((base * multiplier) / 100.0) * 100)
    retail = max(retail, 700)
    return retail, display_unit


def _load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _dedupe_by_product_id(rows: list[dict]) -> list[dict]:
    m = {}
    for r in rows:
        pid = r.get("product_id")
        if pid:
            m[pid] = r
    return list(m.values())


def _stock_status() -> str:
    # in_stock 70%, low_stock 20%, out_of_stock 10%
    p = random.random()
    if p < 0.7:
        return "in_stock"
    if p < 0.9:
        return "low_stock"
    return "out_of_stock"


def _pick_stores(limit: int) -> list[str]:
    stores = _load_json(STORE_FILE)
    store_ids = [s["store_id"] for s in stores if s.get("store_id")]
    if not store_ids:
        raise ValueError("stores.json에서 store_id를 찾을 수 없습니다.")
    if limit <= len(store_ids):
        return random.sample(store_ids, limit)
    return [random.choice(store_ids) for _ in range(limit)]


def generate(target_count: int, seed: int) -> list[dict]:
    random.seed(seed)

    price_file = _latest_price_file()
    payload = _load_json(price_file)
    rows = payload.get("rows", [])

    # 품목명이 없는 row 제거
    rows = [r for r in rows if str(r.get("item_name", "")).strip()]
    if not rows:
        raise ValueError("가격 데이터 rows가 비어 있습니다.")

    products: list[dict] = []
    stores = _pick_stores(target_count)

    adjectives = ["국내산", "신선", "제철", "프리미엄", "특가"]

    for i in range(target_count):
        src = random.choice(rows)
        item_name = _normalize_item_name(str(src.get("item_name", "")))
        retail_price, retail_unit = _retail_price(src)

        # 점포별 편차 반영 (±12%)
        factor = random.uniform(0.88, 1.12)
        price = int(round(retail_price * factor / 100.0) * 100)
        price = max(price, 700)

        product_name = f"{random.choice(adjectives)} {item_name} {retail_unit}"
        products.append(
            {
                "product_id": str(uuid.uuid4()),
                "store_id": stores[i],
                "product_name": product_name,
                "price": price,
                "stock_status": _stock_status(),
                "image_url": None,
            }
        )

    return products


def main() -> None:
    parser = argparse.ArgumentParser(description="가격 API 기반 Product 모킹 대량 생성")
    parser.add_argument("--target-count", type=int, default=180, help="생성할 상품 수")
    parser.add_argument("--seed", type=int, default=42, help="랜덤 시드")
    parser.add_argument("--replace", action="store_true", help="기존 agent_demo/products.json 완전 교체")
    args = parser.parse_args()

    new_rows = generate(target_count=args.target_count, seed=args.seed)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    if args.replace:
        merged = new_rows
    else:
        existing = _load_json(OUT_FILE)
        merged = _dedupe_by_product_id(existing + new_rows)

    OUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] 신규 생성: {len(new_rows)}건")
    print(f"[SAVED] {OUT_FILE} (총 {len(merged)}건)")


if __name__ == "__main__":
    main()
