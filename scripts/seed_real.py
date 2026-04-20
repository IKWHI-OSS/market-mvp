"""
seed_real.py — KAMIS 실제 가격 데이터를 MarketPrice 테이블에 삽입합니다.
Product.price(상인 판매가)는 변경하지 않습니다.
데이터 소스: data/real/kamis_prices_YYYYMMDD.json
"""

import os
import json
import glob
import uuid
import datetime
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "market_mvp"),
}

REAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "real")

ITEM_CODE_MAP = {
    "쌀":       "111",
    "배추":     "214",
    "무":       "215",
    "양파":     "216",
    "마늘":     "217",
    "대파":     "232",
    "고추":     "244",
    "사과":     "412",
    "배":       "413",
    "돼지고기": "514",
    "쇠고기":   "515",
}


def parse_price(price_str: str):
    if not price_str or price_str.strip() in ("-", ""):
        return None
    try:
        return int(price_str.replace(",", "").strip())
    except ValueError:
        return None


def load_kamis_file():
    files = sorted(glob.glob(os.path.join(REAL_DIR, "kamis_prices_*.json")))
    if not files:
        print("[SKIP] KAMIS 가격 파일 없음")
        return "", []
    latest = files[-1]
    print(f"[LOAD] {latest}")
    with open(latest, encoding="utf-8") as f:
        return latest, json.load(f)


def seed_market_prices(conn):
    cur = conn.cursor()

    filename, kamis_data = load_kamis_file()
    if not kamis_data:
        return

    basename = os.path.basename(filename)
    date_str = basename.replace("kamis_prices_", "").replace(".json", "")
    price_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()

    # 전체 rows를 메모리에 수집 후 한 번에 INSERT
    rows = []
    seen = set()

    for item_entry in kamis_data:
        item_label = item_entry["item_name"]
        item_code  = ITEM_CODE_MAP.get(item_label, "000")

        for row in item_entry["data"]:
            name = row.get("item_name", "").strip()
            unit = row.get("unit", "").strip()
            if not name or not unit:
                continue

            # 중복 제거 (item_code + name + price_date)
            key = (item_code, name, str(price_date))
            if key in seen:
                continue
            seen.add(key)

            rows.append((
                str(uuid.uuid4()),
                name,
                item_code,
                unit,
                price_date,
                parse_price(row.get("dpr1")),
                parse_price(row.get("dpr2")),
                parse_price(row.get("dpr3")),
                parse_price(row.get("dpr4")),
            ))

    print(f"[INSERT] {len(rows)}건 일괄 삽입 중...")

    # executemany로 한 번에 전송
    cur.executemany(
        """
        INSERT IGNORE INTO MarketPrice
          (market_price_id, item_name, kamis_item_code, unit,
           price_date, retail_price, prev_day_price,
           prev_month_price, prev_year_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        rows,
    )

    conn.commit()
    cur.close()
    print(f"[OK] MarketPrice 삽입 완료 — {len(rows)}건")
    print(f"     기준일: {price_date} | Product.price는 변경되지 않았습니다.")


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        seed_market_prices(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
