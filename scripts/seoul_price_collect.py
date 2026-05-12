"""
seoul_price_collect.py
서울 열린데이터광장 API(서울시농수산식품공사 주요품목가격)에서 가격 데이터를 수집해
data/real/seoul_prices_YYYYMMDD.json 으로 저장한다.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        p = Path(__file__).parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _extract_rows(payload: dict, service_name: str) -> list[dict]:
    block = payload.get(service_name)
    if isinstance(block, dict) and isinstance(block.get("row"), list):
        return block["row"]
    for _, v in payload.items():
        if isinstance(v, dict) and isinstance(v.get("row"), list):
            return v["row"]
    return []


def collect(service_name: str, start: int, end: int, api_key: str) -> list[dict]:
    base = "http://openapi.seoul.go.kr:8088"
    url = f"{base}/{api_key}/json/{service_name}/{start}/{end}/"
    print(f"[API] GET {url}")

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    rows = _extract_rows(payload, service_name)
    print(f"[OK] rows={len(rows)}")
    return rows


def normalize(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for r in rows:
        item_name = (
            r.get("PUM_MN_A")
            or r.get("PUM_NM")
            or r.get("ITEM_NAME")
            or r.get("PRDLST_NM")
            or r.get("A_NAME")
            or r.get("ITEM_NM")
            or r.get("품목명")
            or ""
        )
        unit = (
            r.get("U_NAME")
            or r.get("UNIT")
            or r.get("STD")
            or r.get("SPEC")
            or r.get("규격")
            or ""
        )
        market_name = (
            r.get("M_NAME")
            or r.get("MRKT_NM")
            or r.get("MARKET_NAME")
            or r.get("시장명")
            or ""
        )
        district = (
            r.get("G_NAME_A")
            or r.get("GU_NM")
            or r.get("SIGNGU_NM")
            or r.get("DISTRICT")
            or r.get("자치구")
            or ""
        )
        price_raw = (
            r.get("AV_P_A")
            or r.get("PRC")
            or r.get("PRICE")
            or r.get("A_PRICE")
            or r.get("금액")
            or r.get("소매가")
            or ""
        )
        as_of = (
            r.get("GET_DATE")
            or r.get("BASE_DE")
            or r.get("P_DATE")
            or r.get("DATE")
            or r.get("기준일")
            or ""
        )

        out.append(
            {
                "item_name": str(item_name).strip(),
                "unit": str(unit).strip(),
                "market_name": str(market_name).strip(),
                "district": str(district).strip(),
                "price_raw": str(price_raw).strip(),
                "as_of": str(as_of).strip(),
                "raw": r,
            }
        )
    return out


def main() -> None:
    _load_dotenv()

    parser = argparse.ArgumentParser(description="서울시 주요품목가격 데이터 수집")
    parser.add_argument("--service-name", required=True, help="서울 열린데이터광장 서비스명")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=1000)
    args = parser.parse_args()

    api_key = os.getenv("SEOUL_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("[ERROR] SEOUL_API_KEY가 .env에 없습니다.")

    rows = collect(args.service_name, args.start, args.end, api_key)
    normalized = normalize(rows)

    out_dir = Path(__file__).parent.parent / "data" / "real"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().strftime("%Y%m%d")
    out_file = out_dir / f"seoul_prices_{today}.json"

    payload = {
        "service_name": args.service_name,
        "collected_at": dt.datetime.now().isoformat(),
        "count": len(normalized),
        "rows": normalized,
    }

    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SAVED] {out_file} (rows={len(normalized)})")


if __name__ == "__main__":
    main()
