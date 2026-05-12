"""
seed_mock_v2.py — data/mock_v2/ 의 확장 모킹 데이터 + 신규 시드(MarketPrice, ProductPriceHistory, Story)를
market_mvp DB에 일괄 적재한다.

INSERT IGNORE 기반이므로 동일 PK·UNIQUE 충돌 시 건너뛴다 → 멱등 실행 가능.

사용:
  cd /Users/karla/Documents/market-mvp
  python scripts/seed_mock_v2.py            # data/mock_v2/ 사용 (기본)
  MOCK_DIR=data/mock python scripts/seed_mock_v2.py  # 기존 데이터 시드만
"""

import json
import os

import bcrypt
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME",     "market_mvp"),
}

MOCK_DIR = os.path.join(
    os.path.dirname(__file__), "..",
    os.getenv("MOCK_DIR", "data/mock_v2"),
)


def load_json(filename: str) -> list:
    path = os.path.join(MOCK_DIR, filename)
    if not os.path.exists(path):
        print(f"[SKIP] {filename} not found in {MOCK_DIR}")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed(conn) -> None:
    cur = conn.cursor()

    # 1. Market
    rows = load_json("markets.json")
    for m in rows:
        cur.execute(
            "INSERT IGNORE INTO Market (market_id, market_name, address, lat, lng) "
            "VALUES (%s, %s, %s, %s, %s)",
            (m["market_id"], m["market_name"], m["address"], m["lat"], m["lng"]),
        )
    print(f"[OK] Market               : {len(rows):4d}건")

    # 2. User (비밀번호 bcrypt)
    rows = load_json("users.json")
    for u in rows:
        hashed = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt(rounds=12)).decode()
        cur.execute(
            "INSERT IGNORE INTO User (user_id, email, password, role, name) "
            "VALUES (%s, %s, %s, %s, %s)",
            (u["user_id"], u["email"], hashed, u["role"], u["name"]),
        )
    print(f"[OK] User                 : {len(rows):4d}건")

    # 3. Store
    rows = load_json("stores.json")
    for s in rows:
        cur.execute(
            "INSERT IGNORE INTO Store "
            "(store_id, market_id, store_name, zone_label, lat, lng) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (s["store_id"], s["market_id"], s["store_name"],
             s["zone_label"], s.get("lat"), s.get("lng")),
        )
    print(f"[OK] Store                : {len(rows):4d}건")

    # 4. Merchant
    rows = load_json("merchants.json")
    for m in rows:
        cur.execute(
            "INSERT IGNORE INTO Merchant (merchant_id, store_id, user_id, display_name) "
            "VALUES (%s, %s, %s, %s)",
            (m["merchant_id"], m["store_id"], m["user_id"], m["display_name"]),
        )
    print(f"[OK] Merchant             : {len(rows):4d}건")

    # 5. Product
    rows = load_json("products.json")
    for p in rows:
        cur.execute(
            "INSERT IGNORE INTO Product "
            "(product_id, store_id, product_name, category, price, stock_status, image_url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (p["product_id"], p["store_id"], p["product_name"],
             p.get("category"), p["price"], p["stock_status"], p.get("image_url")),
        )
    print(f"[OK] Product              : {len(rows):4d}건")

    # 6. DropEvent
    rows = load_json("drop_events.json")
    for d in rows:
        cur.execute(
            "INSERT IGNORE INTO DropEvent "
            "(drop_id, product_id, store_id, title, expected_at, status, subscriber_count) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (d["drop_id"], d["product_id"], d["store_id"],
             d.get("title"), d["expected_at"], d["status"],
             d.get("subscriber_count", 0)),
        )
    print(f"[OK] DropEvent            : {len(rows):4d}건")

    # 7. CatalogItem
    rows = load_json("catalog_items.json")
    for c in rows:
        title = c.get("title", c.get("title_snapshot", ""))
        cur.execute(
            "INSERT IGNORE INTO CatalogItem "
            "(catalog_item_id, market_id, store_id, product_id, item_type, "
            " title, title_snapshot, image_snapshot, price_snapshot) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (c["catalog_item_id"], c["market_id"],
             c.get("store_id"), c.get("product_id"),
             c["item_type"], title, title,
             c.get("image_snapshot"), c.get("price_snapshot")),
        )
    print(f"[OK] CatalogItem          : {len(rows):4d}건")

    # 8. ShoppingList
    rows = load_json("shopping_lists.json")
    for s in rows:
        cur.execute(
            "INSERT IGNORE INTO ShoppingList (shopping_list_id, user_id, title) "
            "VALUES (%s, %s, %s)",
            (s["shopping_list_id"], s["user_id"], s["title"]),
        )
    print(f"[OK] ShoppingList         : {len(rows):4d}건")

    # 9. ShoppingListItem
    rows = load_json("shopping_list_items.json")
    for i in rows:
        cur.execute(
            "INSERT IGNORE INTO ShoppingListItem "
            "(list_item_id, shopping_list_id, product_id, store_id, "
            " product_name_snapshot, qty, unit, checked, estimated_price) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (i["list_item_id"], i["shopping_list_id"],
             i.get("product_id"), i.get("store_id"),
             i["product_name_snapshot"], i["qty"], i["unit"],
             i.get("checked", 0), i.get("estimated_price")),
        )
    print(f"[OK] ShoppingListItem     : {len(rows):4d}건")

    # 10. RoutePlan
    rows = load_json("route_plans.json")
    for r in rows:
        rj = r["route_json"]
        if not isinstance(rj, str):
            rj = json.dumps(rj, ensure_ascii=False)
        cur.execute(
            "INSERT IGNORE INTO RoutePlan "
            "(route_plan_id, user_id, market_id, route_json, estimated_minutes, distance_meters) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (r["route_plan_id"], r["user_id"], r["market_id"], rj,
             r.get("estimated_minutes"), r.get("distance_meters")),
        )
    print(f"[OK] RoutePlan            : {len(rows):4d}건")

    # 11. Notification
    rows = load_json("notifications.json")
    for n in rows:
        cur.execute(
            "INSERT IGNORE INTO Notification "
            "(notification_id, user_id, type, title, target_type, target_id, is_read) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (n["notification_id"], n["user_id"], n["type"],
             n.get("title", ""), n["target_type"], n["target_id"],
             n.get("is_read", 0)),
        )
    print(f"[OK] Notification         : {len(rows):4d}건")

    # 12. Preorder
    rows = load_json("preorders.json")
    for p in rows:
        cur.execute(
            "INSERT IGNORE INTO Preorder "
            "(preorder_id, user_id, store_id, product_name, qty, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (p["preorder_id"], p["user_id"], p["store_id"],
             p["product_name"], p["qty"], p["status"]),
        )
    print(f"[OK] Preorder             : {len(rows):4d}건")

    # 13. MarketPrice (신규)
    rows = load_json("market_prices.json")
    for mp in rows:
        cur.execute(
            "INSERT IGNORE INTO MarketPrice "
            "(market_price_id, item_name, kamis_item_code, unit, price_date, "
            " retail_price, prev_day_price, prev_month_price, prev_year_price) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (mp["market_price_id"], mp["item_name"], mp["kamis_item_code"],
             mp["unit"], mp["price_date"], mp.get("retail_price"),
             mp.get("prev_day_price"), mp.get("prev_month_price"),
             mp.get("prev_year_price")),
        )
    print(f"[OK] MarketPrice          : {len(rows):4d}건")

    # 14. ProductPriceHistory (신규)
    rows = load_json("product_price_histories.json")
    for h in rows:
        cur.execute(
            "INSERT IGNORE INTO ProductPriceHistory "
            "(history_id, product_id, old_price, new_price, reason, reference_id, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (h["history_id"], h["product_id"], h["old_price"], h["new_price"],
             h["reason"], h.get("reference_id"), h.get("created_at")),
        )
    print(f"[OK] ProductPriceHistory  : {len(rows):4d}건")

    # 15. Story (신규 — Phase 2 ADR-04)
    rows = load_json("stories.json")
    for s in rows:
        cur.execute(
            "INSERT IGNORE INTO Story "
            "(story_id, store_id, merchant_id, title, content, "
            " content_short, content_normal, content_detailed, "
            " tone, selected_length, hashtags_json, interview_text, "
            " fallback_mode, is_published, published_at, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (s["story_id"], s["store_id"], s.get("merchant_id"), s.get("title"),
             s["content"], s.get("content_short"), s.get("content_normal"),
             s.get("content_detailed"), s.get("tone", "친근한"),
             s.get("selected_length", "normal"), s.get("hashtags_json"),
             s.get("interview_text"), s.get("fallback_mode", 0),
             s.get("is_published", 0), s.get("published_at"),
             s.get("created_at")),
        )
    print(f"[OK] Story                : {len(rows):4d}건")

    # 15-b. Story (LLM 생성분 — stories_llm.json, 있으면 추가 적재)
    rows = load_json("stories_llm.json")
    for s in rows:
        cur.execute(
            "INSERT IGNORE INTO Story "
            "(story_id, store_id, merchant_id, title, content, "
            " content_short, content_normal, content_detailed, "
            " tone, selected_length, hashtags_json, interview_text, "
            " fallback_mode, is_published, published_at, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (s["story_id"], s["store_id"], s.get("merchant_id"), s.get("title"),
             s["content"], s.get("content_short"), s.get("content_normal"),
             s.get("content_detailed"), s.get("tone", "친근한"),
             s.get("selected_length", "normal"), s.get("hashtags_json"),
             s.get("interview_text"), s.get("fallback_mode", 0),
             s.get("is_published", 0), s.get("published_at"),
             s.get("created_at")),
        )
    print(f"[OK] Story (LLM)          : {len(rows):4d}건")

    conn.commit()
    cur.close()
    print("\n✅ 전체 시딩 완료")


def main() -> None:
    print(f"[CONFIG] MOCK_DIR = {MOCK_DIR}")
    print(f"[CONFIG] DB       = {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print()
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        seed(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
