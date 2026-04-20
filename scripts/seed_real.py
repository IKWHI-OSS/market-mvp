"""
seed_real.py — market_mvp 데이터베이스에 실제 데이터를 삽입합니다.
데이터 소스: data/real/ 디렉터리의 JSON/CSV 파일 (KAMIS 수집 데이터 등)
"""

import os
import json
import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "market_mvp",
}

REAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "real")


def load_json(filename: str) -> list:
    path = os.path.join(REAL_DIR, filename)
    if not os.path.exists(path):
        print(f"[SKIP] {filename} not found")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_products(conn):
    cur = conn.cursor()
    products = load_json("products.json")
    inserted = 0
    for p in products:
        cur.execute(
            "INSERT IGNORE INTO Product "
            "(product_id, store_id, product_name, price, stock_status, image_url) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                p["product_id"],
                p["store_id"],
                p["product_name"],
                p["price"],
                p.get("stock_status", "in_stock"),
                p.get("image_url"),
            ),
        )
        inserted += 1
    conn.commit()
    print(f"[OK] Inserted {inserted} products")
    cur.close()


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        seed_products(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
