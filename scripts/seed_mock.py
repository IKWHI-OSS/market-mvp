"""
seed_mock.py — market_mvp 데이터베이스에 목(Mock) 데이터를 삽입합니다.
데이터 소스: data/mock/ 디렉터리의 JSON 파일
"""

import os
import json
import argparse
import bcrypt
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

MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "mock")
MOCK_PROFILE = os.getenv("MOCK_PROFILE", "").strip()

def _dedupe_rows(rows: list[dict]) -> list[dict]:
    if not rows:
        return rows
    # *_id 형태의 PK를 우선 dedupe 키로 사용
    id_key = None
    sample = rows[0]
    for k in sample.keys():
        if k.endswith("_id"):
            id_key = k
            break
    if not id_key:
        return rows
    out = {}
    for row in rows:
        key = row.get(id_key)
        if key is None:
            continue
        out[key] = row
    return list(out.values())


def load_json(filename: str, profile: str = "") -> list:
    base_path = os.path.join(MOCK_DIR, filename)
    base_rows = []
    if os.path.exists(base_path):
        with open(base_path, encoding="utf-8") as f:
            base_rows = json.load(f)

    if not profile:
        if not base_rows:
            print(f"[SKIP] {filename} not found")
        return base_rows

    profile_path = os.path.join(MOCK_DIR, "profiles", profile, filename)
    profile_rows = []
    if os.path.exists(profile_path):
        with open(profile_path, encoding="utf-8") as f:
            profile_rows = json.load(f)

    if not base_rows and not profile_rows:
        print(f"[SKIP] {filename} not found (base/profile)")
        return []

    merged = _dedupe_rows(base_rows + profile_rows)
    if profile_rows:
        print(f"[PROFILE:{profile}] {filename} +{len(profile_rows)}건 병합")
    return merged


def seed(conn, profile: str = ""):
    cur = conn.cursor()

    # 1. Market
    markets = load_json("markets.json", profile)
    for m in markets:
        cur.execute(
            "INSERT IGNORE INTO Market (market_id, market_name, address, lat, lng) "
            "VALUES (%s, %s, %s, %s, %s)",
            (m["market_id"], m["market_name"], m["address"], m["lat"], m["lng"]),
        )
    print(f"[OK] Market          : {len(markets)}건")

    # 2. User
    users = load_json("users.json", profile)
    for u in users:
        hashed_pw = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt(rounds=12)).decode()
        cur.execute(
            "INSERT IGNORE INTO User (user_id, email, password, role, name) "
            "VALUES (%s, %s, %s, %s, %s)",
            (u["user_id"], u["email"], hashed_pw, u["role"], u["name"]),
        )
    print(f"[OK] User            : {len(users)}건")
    print("     테스트 계정 (모두 비밀번호: password123)")
    print("       consumer01@market.com  (소비자)")
    print("       merchant01@market.com  (상인)")

    # 3. Store
    stores = load_json("stores.json", profile)
    for s in stores:
        cur.execute(
            "INSERT IGNORE INTO Store "
            "(store_id, market_id, store_name, zone_label, lat, lng) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (s["store_id"], s["market_id"], s["store_name"],
             s["zone_label"], s.get("lat"), s.get("lng")),
        )
    print(f"[OK] Store           : {len(stores)}건")

    # 4. Merchant
    merchants = load_json("merchants.json", profile)
    for m in merchants:
        cur.execute(
            "INSERT IGNORE INTO Merchant (merchant_id, store_id, user_id, display_name) "
            "VALUES (%s, %s, %s, %s)",
            (m["merchant_id"], m["store_id"], m["user_id"], m["display_name"]),
        )
    print(f"[OK] Merchant        : {len(merchants)}건")

    # 5. Product
    products = load_json("products.json", profile)
    for p in products:
        cur.execute(
            "INSERT IGNORE INTO Product "
            "(product_id, store_id, product_name, price, stock_status, image_url) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (p["product_id"], p["store_id"], p["product_name"],
             p["price"], p["stock_status"], p.get("image_url")),
        )
    print(f"[OK] Product         : {len(products)}건")

    # 6. DropEvent
    drops = load_json("drop_events.json", profile)
    for d in drops:
        cur.execute(
            "INSERT IGNORE INTO DropEvent (drop_id, product_id, store_id, expected_at, status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (d["drop_id"], d["product_id"], d["store_id"],
             d["expected_at"], d["status"]),
        )
    print(f"[OK] DropEvent       : {len(drops)}건")

    # 7. CatalogItem
    catalogs = load_json("catalog_items.json", profile)
    for c in catalogs:
        title = c.get("title", c.get("title_snapshot", ""))
        cur.execute(
            "INSERT IGNORE INTO CatalogItem "
            "(catalog_item_id, market_id, item_type, title, title_snapshot, image_snapshot, price_snapshot) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (c["catalog_item_id"], c["market_id"], c["item_type"],
             title, title, c.get("image_snapshot"), c.get("price_snapshot")),
        )
    print(f"[OK] CatalogItem     : {len(catalogs)}건")

    # 8. ShoppingList
    slists = load_json("shopping_lists.json", profile)
    for s in slists:
        cur.execute(
            "INSERT IGNORE INTO ShoppingList (shopping_list_id, user_id, title) "
            "VALUES (%s, %s, %s)",
            (s["shopping_list_id"], s["user_id"], s["title"]),
        )
    print(f"[OK] ShoppingList    : {len(slists)}건")

    # 9. ShoppingListItem
    items = load_json("shopping_list_items.json", profile)
    for i in items:
        cur.execute(
            "INSERT IGNORE INTO ShoppingListItem "
            "(list_item_id, shopping_list_id, product_name_snapshot, qty, unit, checked) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (i["list_item_id"], i["shopping_list_id"], i["product_name_snapshot"],
             i["qty"], i["unit"], i.get("checked", 0)),
        )
    print(f"[OK] ShoppingListItem: {len(items)}건")

    # 10. RoutePlan
    routes = load_json("route_plans.json", profile)
    for r in routes:
        route_json = r["route_json"]
        if not isinstance(route_json, str):
            route_json = json.dumps(route_json, ensure_ascii=False)
        cur.execute(
            "INSERT IGNORE INTO RoutePlan (route_plan_id, user_id, market_id, route_json) "
            "VALUES (%s, %s, %s, %s)",
            (r["route_plan_id"], r["user_id"], r["market_id"], route_json),
        )
    print(f"[OK] RoutePlan       : {len(routes)}건")

    # 11. Notification
    notifs = load_json("notifications.json", profile)
    for n in notifs:
        cur.execute(
            "INSERT IGNORE INTO Notification "
            "(notification_id, user_id, type, title, target_type, target_id, is_read) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (n["notification_id"], n["user_id"], n["type"],
             n.get("title", ""), n["target_type"], n["target_id"],
             n.get("is_read", 0)),
        )
    print(f"[OK] Notification    : {len(notifs)}건")

    # 12. Preorder
    preorders = load_json("preorders.json", profile)
    for p in preorders:
        cur.execute(
            "INSERT IGNORE INTO Preorder "
            "(preorder_id, user_id, store_id, product_name, qty, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (p["preorder_id"], p["user_id"], p["store_id"],
             p["product_name"], p["qty"], p["status"]),
        )
    print(f"[OK] Preorder        : {len(preorders)}건")

    conn.commit()
    cur.close()
    profile_txt = profile if profile else "base"
    print(f"\n✅ 전체 시딩 완료 (profile={profile_txt})")


def main():
    parser = argparse.ArgumentParser(description="Mock 데이터 시딩")
    parser.add_argument(
        "--profile",
        default=MOCK_PROFILE,
        help="data/mock/profiles/<profile> 데이터 병합 (예: consumer_demo, merchant_demo, agent_demo)",
    )
    args = parser.parse_args()

    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        seed(conn, args.profile)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
