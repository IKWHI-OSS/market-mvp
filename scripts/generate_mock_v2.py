"""
generate_mock_v2.py — 모킹 데이터를 10배(±) 규모로 확장 생성한다.

- 입력  : data/mock/*.json (기존 데이터, 보존)
- 출력  : data/mock_v2/*.json (확장 데이터, 기존 데이터 포함)
- 시드  : random.seed(42) — 재현 가능
- 신규  : market_prices.json, product_price_histories.json, stories.json

규모 (기존 → 확장)
  Market           1 → 10    (서울 주요 전통시장 9곳 추가)
  User             5 → 50    (consumer 22, merchant 25, operator 3)
  Store           10 → 100   (시장당 8~12개)
  Merchant        10 → 100   (Store와 1:1, user_id는 25명에 분산)
  Product         48 → 480   (Store당 4~6개)
  DropEvent       12 → 120
  CatalogItem     18 → 180
  ShoppingList     3 → 30
  ShoppingListItem 15 → 150
  RoutePlan        3 → 30
  Notification     6 → 60
  Preorder         2 → 20

신규 시드
  MarketPrice            7품목 × 30일 = 210
  ProductPriceHistory    Product 30%에 1~3건 = 약 200
  Story                  Store당 1~3개 = 약 200 (50%는 published)
"""
from __future__ import annotations

import json
import os
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data" / "mock"
DST_DIR = ROOT / "data" / "mock_v2"
DST_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ─────────────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────────────

def load(name: str) -> list:
    path = SRC_DIR / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def dump(name: str, data: list) -> None:
    path = DST_DIR / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  → {name:32s} {len(data):4d}건")


def uid(prefix: str, n: int) -> str:
    """짧고 결정성 있는 UUID 형식 ID."""
    rand_hex = uuid.UUID(int=random.getrandbits(128)).hex[:16]
    return f"{prefix}{n:06d}-{rand_hex[:4]}-4{rand_hex[4:7]}-a{rand_hex[7:10]}-{rand_hex[10:16]}{rand_hex[:6]}"


# ─────────────────────────────────────────────────────────────────────
# 마스터 데이터 (서울 전통시장)
# ─────────────────────────────────────────────────────────────────────

EXTRA_MARKETS = [
    {"name": "광장시장",   "addr": "서울특별시 종로구 창경궁로 88",         "lat": 37.5708, "lng": 126.9999},
    {"name": "통인시장",   "addr": "서울특별시 종로구 자하문로15길 18",      "lat": 37.5808, "lng": 126.9698},
    {"name": "남대문시장", "addr": "서울특별시 중구 남대문시장길 21",        "lat": 37.5599, "lng": 126.9772},
    {"name": "동대문시장", "addr": "서울특별시 중구 을지로44길 11",          "lat": 37.5663, "lng": 127.0085},
    {"name": "경동시장",   "addr": "서울특별시 동대문구 고산자로 472",       "lat": 37.5805, "lng": 127.0399},
    {"name": "영등포시장", "addr": "서울특별시 영등포구 영등포로 156",       "lat": 37.5180, "lng": 126.9078},
    {"name": "노량진수산시장", "addr": "서울특별시 동작구 노들로 674",       "lat": 37.5126, "lng": 126.9418},
    {"name": "방배시장",   "addr": "서울특별시 서초구 방배중앙로 73",        "lat": 37.4815, "lng": 126.9933},
    {"name": "암사종합시장", "addr": "서울특별시 강동구 올림픽로98길 47",     "lat": 37.5519, "lng": 127.1262},
]

ZONE_LABELS = ["A구역", "B구역", "C구역", "D구역", "E구역", "F구역"]

STORE_PROFILES = [
    ("신선야채",     "vegetable", ["국내산 시금치 200g", "강원도 감자 1kg", "충남 당근 500g", "유기농 상추 100g", "국내산 고구마 1kg", "친환경 양배추 1통", "햇양파 1.5kg", "느타리버섯 200g", "국내산 깻잎 100g", "대파 1단"]),
    ("채소마트",     "vegetable", ["청양고추 500g", "방울토마토 500g", "오이 5개", "애호박 2개", "쪽파 1단", "마늘 200g", "생강 100g", "콩나물 300g", "두부 1모", "가지 3개"]),
    ("과일나라",     "fruit",     ["제주 감귤 3kg", "샤인머스캣 500g", "후지 사과 5개", "신고 배 5개", "딸기 500g", "참외 5개", "수박 1통", "단감 5개", "자두 500g", "복숭아 5개"]),
    ("달콤 과일",    "fruit",     ["블루베리 200g", "체리 500g", "키위 5개", "바나나 1송이", "파인애플 1개", "망고 3개", "포도 1kg", "방울토마토 500g", "참외 5개", "복숭아 5개"]),
    ("수산",         "seafood",   ["고등어 1손", "갈치 2마리", "오징어 2마리", "꽃게 1kg", "새우 500g", "전복 500g", "낙지 2마리", "조기 5마리", "굴 500g", "홍합 1kg"]),
    ("해산물",       "seafood",   ["광어회 300g", "참치회 200g", "연어회 250g", "건어물 모듬 200g", "멸치 200g", "쥐포 100g", "바다장어 1마리", "꼬막 500g", "해삼 200g", "성게알 100g"]),
    ("정육",         "meat",      ["한우 등심 200g", "한우 갈비 600g", "삼겹살 600g", "목살 500g", "닭다리살 500g", "소불고기 500g", "돼지갈비 600g", "닭가슴살 500g", "닭날개 500g", "양고기 300g"]),
    ("반찬가게",     "banchan",   ["김치 1kg", "깍두기 500g", "콩자반 200g", "멸치볶음 200g", "오이무침 300g", "잡채 300g", "감자조림 300g", "어묵볶음 300g", "두부조림 300g", "장아찌 200g"]),
    ("생활잡화",     "misc",      ["주방세제 500ml", "고무장갑 1켤레", "밀폐용기 3종", "행주 5장", "주방가위", "양념통 세트", "도시락통 1개", "수세미 5개", "키친타올 6롤", "비닐백 100매"]),
    ("건어물",       "dried",     ["멸치 200g", "다시마 100g", "건오징어 3마리", "마른새우 100g", "북어채 200g", "파래 50g", "김 10장", "건미역 100g", "건문어 1마리", "건홍합 100g"]),
    ("떡집",         "rice_cake", ["가래떡 1kg", "송편 20개", "절편 500g", "백설기 500g", "쑥떡 500g", "콩떡 500g", "찹쌀떡 10개", "꿀떡 20개", "약식 500g", "인절미 500g"]),
    ("분식",         "snack",     ["김밥 1줄", "떡볶이 1인분", "순대 300g", "튀김 모듬", "어묵 5꼬치", "쫄면 1인분", "라볶이 1인분", "오뎅탕 500ml", "만두 10개", "호떡 5개"]),
]

CONSUMER_NAMES = ["김지연", "이민준", "박서연", "정하윤", "최예준", "강시우", "윤지호", "조하린", "장유나", "임채원", "한도윤", "오은서", "신주원", "권태민", "황소율", "백지민", "남궁민", "서다은", "허지안", "문서진", "양수아", "노유빈"]
MERCHANT_NAMES = ["박철수", "최영희", "김상도", "이순자", "장만덕", "홍금례", "강옥자", "정만호", "서태식", "조명자", "권춘식", "임병국", "신점례", "오만식", "황복례", "남기수", "백상철", "민영자", "윤복순", "한상필", "유재기", "노덕례", "안종철", "고만수", "손분이"]
OPERATOR_NAMES = ["시스템관리자", "운영팀A", "운영팀B"]

KAMIS_ITEMS = [
    # ── 채소 (8) — 코드 1xx
    {"code": "112", "category": "채소",  "name": "배추/포기",     "unit": "1포기", "base_price": 4500},
    {"code": "151", "category": "채소",  "name": "무/일반",       "unit": "1개",   "base_price": 2200},
    {"code": "152", "category": "채소",  "name": "당근",          "unit": "1kg",   "base_price": 3800},
    {"code": "153", "category": "채소",  "name": "양파",          "unit": "1.5kg", "base_price": 4200},
    {"code": "154", "category": "채소",  "name": "대파",          "unit": "1단",   "base_price": 2800},
    {"code": "155", "category": "채소",  "name": "마늘/깐마늘",   "unit": "1kg",   "base_price": 12000},
    {"code": "156", "category": "채소",  "name": "청양고추",      "unit": "100g",  "base_price": 1800},
    {"code": "157", "category": "채소",  "name": "시금치",        "unit": "200g",  "base_price": 2500},
    # ── 과일 (8) — 코드 2xx, 4xx
    {"code": "214", "category": "과일",  "name": "사과/후지",     "unit": "10개",  "base_price": 25000},
    {"code": "215", "category": "과일",  "name": "배/신고",       "unit": "10개",  "base_price": 32000},
    {"code": "216", "category": "과일",  "name": "감귤/제주",     "unit": "3kg",   "base_price": 12000},
    {"code": "217", "category": "과일",  "name": "샤인머스캣",    "unit": "500g",  "base_price": 12000},
    {"code": "218", "category": "과일",  "name": "딸기/설향",     "unit": "500g",  "base_price": 9000},
    {"code": "219", "category": "과일",  "name": "수박/일반",     "unit": "1통",   "base_price": 22000},
    {"code": "421", "category": "과일",  "name": "감/단감",       "unit": "10개",  "base_price": 18000},
    {"code": "422", "category": "과일",  "name": "복숭아/백도",   "unit": "5개",   "base_price": 11000},
    # ── 수산물 (7) — 코드 6xx
    {"code": "601", "category": "수산물","name": "고등어/국산",   "unit": "1손",   "base_price": 6000},
    {"code": "602", "category": "수산물","name": "갈치/국산",     "unit": "1마리", "base_price": 8500},
    {"code": "603", "category": "수산물","name": "오징어/국산",   "unit": "1마리", "base_price": 4500},
    {"code": "604", "category": "수산물","name": "꽃게/암꽃게",   "unit": "1kg",   "base_price": 28000},
    {"code": "605", "category": "수산물","name": "흰다리새우",    "unit": "500g",  "base_price": 18000},
    {"code": "606", "category": "수산물","name": "광어회/활어",   "unit": "300g",  "base_price": 22000},
    {"code": "607", "category": "수산물","name": "굴/생굴",       "unit": "500g",  "base_price": 12000},
    # ── 육류 (7) — 코드 5xx
    {"code": "501", "category": "육류",  "name": "한우/등심",     "unit": "200g",  "base_price": 28000},
    {"code": "502", "category": "육류",  "name": "한우/갈비",     "unit": "600g",  "base_price": 48000},
    {"code": "503", "category": "육류",  "name": "삼겹살/국산",   "unit": "600g",  "base_price": 18000},
    {"code": "504", "category": "육류",  "name": "목살/국산",     "unit": "500g",  "base_price": 12000},
    {"code": "505", "category": "육류",  "name": "닭다리살",      "unit": "500g",  "base_price": 6500},
    {"code": "506", "category": "육류",  "name": "닭가슴살",      "unit": "500g",  "base_price": 6000},
    {"code": "507", "category": "육류",  "name": "소불고기/양념", "unit": "500g",  "base_price": 16000},
]

# 상품명 → KAMIS 코드 매칭 (가격 정책 매칭용)
PRODUCT_KAMIS_KEYWORD = {
    # 채소
    "배추": "112", "무": "151", "당근": "152", "양파": "153", "대파": "154",
    "마늘": "155", "고추": "156", "시금치": "157",
    # 과일
    "사과": "214", "후지": "214", "배": "215", "신고": "215", "감귤": "216",
    "샤인": "217", "머스캣": "217", "딸기": "218", "수박": "219",
    "감": "421", "단감": "421", "복숭아": "422",
    # 수산물
    "고등어": "601", "갈치": "602", "오징어": "603", "꽃게": "604",
    "새우": "605", "광어": "606", "굴": "607",
    # 육류
    "한우": "501", "등심": "501", "갈비": "502", "삼겹살": "503", "목살": "504",
    "닭다리": "505", "닭가슴": "506", "닭날개": "505", "불고기": "507",
}


# ─────────────────────────────────────────────────────────────────────
# 1. Market 확장
# ─────────────────────────────────────────────────────────────────────

def expand_markets(existing: list) -> list:
    out = list(existing)
    for i, m in enumerate(EXTRA_MARKETS, start=2):
        out.append({
            "market_id":   f"f{i:01d}a2b3c4-d5e6-4789-a012-b3c4d5e6f7{i:02d}",
            "market_name": m["name"],
            "address":     m["addr"],
            "lat":         m["lat"],
            "lng":         m["lng"],
        })
    return out


# ─────────────────────────────────────────────────────────────────────
# 2. User 확장
# ─────────────────────────────────────────────────────────────────────

def expand_users(existing: list) -> list:
    out = list(existing)
    base_email = "{role}{n:02d}@market.com"
    # consumer 추가 (기존 2 → 22)
    for i in range(3, 23):
        out.append({
            "user_id":  f"a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7{i+10:02d}",
            "email":    base_email.format(role="consumer", n=i),
            "password": "password123",
            "role":     "consumer",
            "name":     CONSUMER_NAMES[i-1] if i-1 < len(CONSUMER_NAMES) else f"소비자{i:02d}",
        })
    # merchant 추가 (기존 2 → 25)
    for i in range(3, 26):
        out.append({
            "user_id":  f"b1b2c3d4-e5f6-4789-a012-b3c4d5e6f7{i+30:02d}",
            "email":    base_email.format(role="merchant", n=i),
            "password": "password123",
            "role":     "merchant",
            "name":     MERCHANT_NAMES[i-1] if i-1 < len(MERCHANT_NAMES) else f"상인{i:02d}",
        })
    # operator 추가 (기존 1 → 3)
    for i in range(2, 4):
        out.append({
            "user_id":  f"c1b2c3d4-e5f6-4789-a012-b3c4d5e6f7{i+50:02d}",
            "email":    base_email.format(role="operator", n=i),
            "password": "password123",
            "role":     "operator",
            "name":     OPERATOR_NAMES[i-1] if i-1 < len(OPERATOR_NAMES) else f"운영자{i:02d}",
        })
    return out


# ─────────────────────────────────────────────────────────────────────
# 3. Store 확장
# ─────────────────────────────────────────────────────────────────────

def expand_stores(existing: list, markets: list) -> list:
    out = list(existing)
    counter = len(existing) + 1
    # 기존 시장(망원) 외 모든 시장에 8~12개씩 점포 생성
    for m in markets[1:]:
        n_stores = random.randint(8, 12)
        used_profiles = random.sample(STORE_PROFILES, k=min(n_stores, len(STORE_PROFILES)))
        for prof_idx, profile in enumerate(used_profiles):
            store_name_prefix = m["market_name"].replace("시장", "")
            store_name = f"{store_name_prefix} {profile[0]}"
            out.append({
                "store_id":   f"d1{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "market_id":  m["market_id"],
                "store_name": store_name,
                "zone_label": random.choice(ZONE_LABELS),
                "lat":        round(m["lat"] + random.uniform(-0.0008, 0.0008), 7),
                "lng":        round(m["lng"] + random.uniform(-0.0008, 0.0008), 7),
                "_profile":   profile[1],
                "_products":  profile[2],
            })
            counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 4. Merchant 확장 (Store 1:1, user_id 분산)
# ─────────────────────────────────────────────────────────────────────

def expand_merchants(existing: list, stores: list, users: list) -> list:
    out = list(existing)
    merchant_users = [u for u in users if u["role"] == "merchant"]
    existing_store_ids = {m["store_id"] for m in existing}
    counter = len(existing) + 1
    for s in stores:
        if s["store_id"] in existing_store_ids:
            continue
        u = random.choice(merchant_users)
        out.append({
            "merchant_id":  f"e1{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
            "store_id":     s["store_id"],
            "user_id":      u["user_id"],
            "display_name": f"{s['store_name']} 사장님",
        })
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 5. Product 확장 (점포당 4~6개)
# ─────────────────────────────────────────────────────────────────────

CATEGORY_BY_PROFILE = {
    "vegetable": "채소", "fruit": "과일", "seafood": "수산",
    "meat": "정육", "banchan": "반찬", "misc": "잡화",
    "dried": "건어물", "rice_cake": "떡", "snack": "분식",
}

def expand_products(existing: list, stores: list) -> list:
    out = list(existing)
    existing_store_ids = {p["store_id"] for p in existing}
    counter = len(existing) + 1
    for s in stores:
        # 기존 데이터에 있는 store는 건너뜀
        if s["store_id"] in existing_store_ids and not s.get("_products"):
            continue
        product_pool = s.get("_products", [])
        if not product_pool:
            continue
        n = random.randint(4, 6)
        chosen = random.sample(product_pool, k=min(n, len(product_pool)))
        for name in chosen:
            base = random.choice([1500, 1800, 2500, 3000, 3500, 4500, 5500, 7500, 9500, 12000, 15000, 18000, 25000])
            stock_status = random.choices(
                ["in_stock", "low_stock", "out_of_stock"],
                weights=[78, 18, 4],
            )[0]
            out.append({
                "product_id":   f"p1{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "store_id":     s["store_id"],
                "product_name": name,
                "category":     CATEGORY_BY_PROFILE.get(s.get("_profile", ""), "기타"),
                "price":        base,
                "stock_status": stock_status,
                "image_url":    None,
            })
            counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 6. DropEvent 확장
# ─────────────────────────────────────────────────────────────────────

def expand_drops(existing: list, products: list) -> list:
    out = list(existing)
    counter = len(existing) + 1
    today = datetime(2026, 5, 10, 7, 0, 0)
    target_total = 120
    while len(out) < target_total:
        p = random.choice(products)
        offset_hr = random.randint(-72, 72)
        expected = today + timedelta(hours=offset_hr)
        status = random.choices(
            ["scheduled", "arrived", "sold_out"],
            weights=[55, 30, 15],
        )[0]
        out.append({
            "drop_id":         f"dr{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
            "product_id":      p["product_id"],
            "store_id":        p["store_id"],
            "title":           f"{p['product_name']} {'특가' if random.random() < 0.4 else '직송'} 입고",
            "expected_at":     expected.strftime("%Y-%m-%d %H:%M:%S"),
            "status":          status,
            "subscriber_count": random.randint(0, 25),
        })
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 7. CatalogItem 확장
# ─────────────────────────────────────────────────────────────────────

def expand_catalog_items(existing: list, markets: list, stores: list, products: list, drops: list) -> list:
    out = list(existing)
    counter = len(existing) + 1
    target_total = 180
    while len(out) < target_total:
        kind = random.choices(["drop", "event", "store_spotlight"], weights=[55, 25, 20])[0]
        m = random.choice(markets)
        if kind == "drop":
            d = random.choice(drops)
            p_match = next((pp for pp in products if pp["product_id"] == d["product_id"]), None)
            title = f"오늘 새벽 {p_match['product_name'] if p_match else '상품'} 입고"
            price = (p_match or {}).get("price")
            entry = {
                "catalog_item_id": f"ca{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "market_id":       m["market_id"],
                "store_id":        d["store_id"],
                "product_id":      d["product_id"],
                "item_type":       "drop",
                "title":           title,
                "title_snapshot":  title,
                "image_snapshot":  None,
                "price_snapshot":  price,
            }
        elif kind == "event":
            event_titles = [
                f"{m['market_name']} 봄맞이 특가전",
                f"{m['market_name']} 야시장 — 매주 금요일",
                f"{m['market_name']} 전통주 시음회",
                f"{m['market_name']} 청년 상인 데이",
            ]
            title = random.choice(event_titles)
            entry = {
                "catalog_item_id": f"ca{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "market_id":       m["market_id"],
                "store_id":        None,
                "product_id":      None,
                "item_type":       "event",
                "title":           title,
                "title_snapshot":  title,
                "image_snapshot":  None,
                "price_snapshot":  None,
            }
        else:
            stores_in_market = [s for s in stores if s["market_id"] == m["market_id"]]
            if not stores_in_market:
                continue
            s = random.choice(stores_in_market)
            title = f"{s['store_name']} — 시장이 사랑하는 단골집"
            entry = {
                "catalog_item_id": f"ca{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "market_id":       m["market_id"],
                "store_id":        s["store_id"],
                "product_id":      None,
                "item_type":       "store_spotlight",
                "title":           title,
                "title_snapshot":  title,
                "image_snapshot":  None,
                "price_snapshot":  None,
            }
        out.append(entry)
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 8. ShoppingList + Items 확장
# ─────────────────────────────────────────────────────────────────────

LIST_TITLES = ["주말 장보기", "저녁 식사 준비", "주중 반찬", "손님 초대 메뉴",
               "한 주 식자재", "다이어트 식단", "도시락 재료", "월말 장보기",
               "비빔밥 재료", "찌개 재료", "구이용 식자재", "샐러드 재료"]

def expand_shopping_lists(existing_lists: list, existing_items: list, users: list, products: list) -> tuple[list, list]:
    out_lists = list(existing_lists)
    out_items = list(existing_items)
    consumers = [u for u in users if u["role"] == "consumer"]
    counter_l = len(existing_lists) + 1
    counter_i = len(existing_items) + 1
    target_lists = 30
    while len(out_lists) < target_lists:
        u = random.choice(consumers)
        list_id = f"sl{counter_l:06d}-e5f6-4789-a012-b3c4d5e6f7{counter_l % 100:02d}"
        out_lists.append({
            "shopping_list_id": list_id,
            "user_id":          u["user_id"],
            "title":            random.choice(LIST_TITLES),
        })
        # 아이템 3~7개
        chosen_products = random.sample(products, k=random.randint(3, 7))
        total = 0
        for p in chosen_products:
            qty = random.randint(1, 3)
            est = p["price"] * qty
            total += est
            out_items.append({
                "list_item_id":          f"li{counter_i:06d}-e5f6-4789-a012-b3c4d5e6f7{counter_i % 100:02d}",
                "shopping_list_id":      list_id,
                "product_id":            p["product_id"],
                "store_id":              p["store_id"],
                "product_name_snapshot": p["product_name"],
                "qty":                   qty,
                "unit":                  "개",
                "checked":               random.choice([0, 0, 0, 1]),
                "estimated_price":       est,
            })
            counter_i += 1
        counter_l += 1
    return out_lists, out_items


# ─────────────────────────────────────────────────────────────────────
# 9. RoutePlan 확장
# ─────────────────────────────────────────────────────────────────────

def expand_route_plans(existing: list, users: list, markets: list, stores: list) -> list:
    out = list(existing)
    consumers = [u for u in users if u["role"] == "consumer"]
    counter = len(existing) + 1
    target = 30
    while len(out) < target:
        u = random.choice(consumers)
        m = random.choice(markets)
        stores_in_market = [s for s in stores if s["market_id"] == m["market_id"]]
        if len(stores_in_market) < 2:
            continue
        chosen = random.sample(stores_in_market, k=min(random.randint(3, 5), len(stores_in_market)))
        steps = [
            {"step": i+1, "store_id": s["store_id"], "store_name": s["store_name"], "zone": s["zone_label"]}
            for i, s in enumerate(chosen)
        ]
        route_json = {
            "route": steps,
            "total_stores": len(steps),
            "total_estimated_minutes": len(steps) * 7,
        }
        out.append({
            "route_plan_id":     f"rp{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
            "user_id":           u["user_id"],
            "market_id":         m["market_id"],
            "route_json":        route_json,
            "estimated_minutes": route_json["total_estimated_minutes"],
            "distance_meters":   len(steps) * 80,
        })
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 10. Notification 확장
# ─────────────────────────────────────────────────────────────────────

NOTIF_TYPES = ["drop_alert", "price_change", "event_start", "system", "preorder_status"]

def expand_notifications(existing: list, users: list, drops: list, products: list, catalog: list) -> list:
    out = list(existing)
    consumers = [u for u in users if u["role"] == "consumer"]
    counter = len(existing) + 1
    target = 60
    while len(out) < target:
        t = random.choice(NOTIF_TYPES)
        u = random.choice(consumers)
        if t == "drop_alert" and drops:
            d = random.choice(drops)
            p = next((pp for pp in products if pp["product_id"] == d["product_id"]), None)
            title = f"{p['product_name'] if p else '상품'} {'입고됨' if d['status']=='arrived' else '입고 예정'}"
            entry = (t, title, "drop", d["drop_id"])
        elif t == "price_change" and products:
            p = random.choice(products)
            old = p["price"] + random.choice([300, 500, 800, 1000])
            title = f"{p['product_name']} 가격 {old:,}원 → {p['price']:,}원으로 인하"
            entry = (t, title, "product", p["product_id"])
        elif t == "event_start" and catalog:
            c = next((cc for cc in catalog if cc["item_type"] == "event"), None)
            if not c:
                continue
            entry = (t, f"{c['title']} 시작", "event", c["catalog_item_id"])
        elif t == "preorder_status":
            entry = (t, "예약 상품이 준비되었습니다", "preorder", None)
        else:
            entry = ("system", "이번 주 인기 상품 리포트가 도착했어요", "market", None)
        out.append({
            "notification_id": f"nt{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
            "user_id":         u["user_id"],
            "type":            entry[0],
            "title":           entry[1],
            "target_type":     entry[2],
            "target_id":       entry[3] or "00000000-0000-0000-0000-000000000000",
            "is_read":         random.choices([0, 1], weights=[65, 35])[0],
        })
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 11. Preorder 확장
# ─────────────────────────────────────────────────────────────────────

PREORDER_STATUSES = ["requested", "confirmed", "ready", "cancelled"]

def expand_preorders(existing: list, users: list, products: list) -> list:
    out = list(existing)
    consumers = [u for u in users if u["role"] == "consumer"]
    counter = len(existing) + 1
    target = 20
    while len(out) < target:
        u = random.choice(consumers)
        p = random.choice(products)
        out.append({
            "preorder_id":  f"po{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
            "user_id":      u["user_id"],
            "store_id":     p["store_id"],
            "product_name": p["product_name"],
            "qty":          random.randint(1, 4),
            "status":       random.choices(PREORDER_STATUSES, weights=[40, 35, 15, 10])[0],
        })
        counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 12. MarketPrice 신규 (KAMIS 7품목 × 30일)
# ─────────────────────────────────────────────────────────────────────

def gen_market_prices() -> list:
    """30품목 × 30일치 = 900건. 카테고리별 변동성 반영."""
    out = []
    today = date(2026, 5, 10)
    # 카테고리별 변동률(±)
    volatility = {
        "곡물":  0.03,  # 안정
        "채소":  0.10,  # 변동성 큼 (날씨/계절)
        "과일":  0.08,
        "수산물": 0.12,  # 변동성 가장 큼 (어획량)
        "육류":  0.05,
    }
    for item in KAMIS_ITEMS:
        base = item["base_price"]
        v = volatility.get(item["category"], 0.07)
        # 일자별 트렌드 (계절성) — sin(2πt/30) 형태로 단순화
        for day_offset in range(30):
            d = today - timedelta(days=29 - day_offset)
            t = day_offset / 30.0
            trend = v * 0.5 * (2 * (t - 0.5))               # 30일에 걸친 선형 추세
            cyclic = v * 0.4 * ((day_offset % 7) / 7 - 0.5)  # 주간 패턴
            noise = random.uniform(-v, v)
            price_today = int(base * (1 + trend + cyclic + noise))
            price_yesterday = int(base * (1 + trend + cyclic + random.uniform(-v, v)))
            price_month_ago = int(base * (1 + random.uniform(-v * 1.5, v * 1.5)))
            price_year_ago = int(base * (1 + random.uniform(-v * 2.5, v * 2.0)))
            out.append({
                "market_price_id": f"mp{len(out)+1:06d}-e5f6-4789-a012-b3c4d5e6f7{len(out) % 100:02d}",
                "item_name":       item["name"],
                "kamis_item_code": item["code"],
                "unit":            item["unit"],
                "price_date":      d.isoformat(),
                "retail_price":    price_today,
                "prev_day_price":  price_yesterday,
                "prev_month_price": price_month_ago,
                "prev_year_price": price_year_ago,
            })
    return out


# ─────────────────────────────────────────────────────────────────────
# 13. ProductPriceHistory 신규
# ─────────────────────────────────────────────────────────────────────

def gen_price_histories(products: list, market_prices: list) -> list:
    """상품 30%에 1~3건 이력 생성. 70% manual / 30% kamis."""
    out = []
    sample = random.sample(products, k=int(len(products) * 0.30))
    counter = 1
    for p in sample:
        n_hist = random.randint(1, 3)
        cur_price = p["price"]
        for k in range(n_hist):
            old = int(cur_price * random.uniform(1.05, 1.20))
            reason = random.choices(["manual", "kamis"], weights=[70, 30])[0]
            ref_id = None
            if reason == "kamis":
                # 매칭되는 KAMIS 코드 시도
                code = None
                for kw, c in PRODUCT_KAMIS_KEYWORD.items():
                    if kw in p["product_name"]:
                        code = c
                        break
                if code:
                    matching = [mp for mp in market_prices if mp["kamis_item_code"] == code]
                    if matching:
                        ref_id = random.choice(matching)["market_price_id"]
            day_offset = random.randint(1, 30) + k * 5
            created_at = (datetime(2026, 5, 10) - timedelta(days=day_offset)).strftime("%Y-%m-%d %H:%M:%S")
            out.append({
                "history_id":   f"ph{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "product_id":   p["product_id"],
                "old_price":    old,
                "new_price":    cur_price,
                "reason":       reason,
                "reference_id": ref_id,
                "created_at":   created_at,
            })
            cur_price = old  # 이전 가격으로 거슬러 올라감
            counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# 14. Story 신규 (Store당 1~3개)
# ─────────────────────────────────────────────────────────────────────

STORY_TONES = ["친근한", "전문적인", "정겨운"]
STORY_TEMPLATES_BY_PROFILE = {
    "vegetable": [
        "{store}는 매일 새벽 가락시장에서 직접 골라온 채소만 진열합니다. 잎이 단단하고 빛이 살아있는 것만 골라드려요.",
        "할머니 손맛의 시작, 신선한 채소 한 단부터 시작됩니다. {store}에서 오늘의 식탁을 준비하세요.",
    ],
    "fruit": [
        "{store}는 산지 직거래 과수원과 직접 계약한 제철 과일만 다룹니다. 당도와 신선도가 다른 이유입니다.",
        "한 입에 퍼지는 단맛, {store}의 자부심입니다. 매일 손으로 골라낸 과일만 진열합니다.",
    ],
    "seafood": [
        "{store}는 새벽 경매장에서 직접 골라온 수산물만 취급합니다. 비린내 없는 신선함, 직접 확인해보세요.",
        "바다의 신선함을 그대로, {store}는 오늘 잡힌 활어와 갓 잡은 해산물만 손님께 드립니다.",
    ],
    "meat": [
        "{store}는 1++ 등급 한우와 직접 발골한 신선한 고기만 다룹니다. 마블링과 색을 직접 보여드릴 수 있어요.",
        "한 끼 식탁의 주인공, 정성껏 손질한 고기만 {store}에서 만나보세요.",
    ],
    "banchan": [
        "{store}의 반찬은 매일 아침 손으로 만들어집니다. 화학조미료 없이, 어머니가 만드시던 그대로의 맛입니다.",
        "오늘 점심도 든든하게, {store}에서 정성껏 무친 반찬으로 식탁을 채우세요.",
    ],
    "misc": [
        "주방의 작은 필수품부터 살림 도구까지, {store}는 30년 경험으로 좋은 물건만 골라 드립니다.",
        "{store}는 가성비 좋은 생활용품을 매일 새로 들여놓습니다. 한 번 들러보시면 단골이 되실 거예요.",
    ],
    "dried": [
        "{store}는 통영·완도산 직송 건어물만 다룹니다. 햇볕에 잘 말린 정직한 맛, 직접 시식해보세요.",
        "오래 두어도 변함없는 깊은 풍미, {store}의 건어물은 어머니의 비법과 함께합니다.",
    ],
    "rice_cake": [
        "{store}는 새벽에 빚어낸 떡만 진열합니다. 쫀득함과 향긋함이 살아있는 진짜 시장 떡을 맛보세요.",
        "잔칫상의 격을 높이는 정성스러운 떡, {store}에서 매일 빚어 드립니다.",
    ],
    "snack": [
        "퇴근길의 위로, {store}의 떡볶이와 김밥은 매일 그날 만든 재료로만 조리합니다.",
        "{store}는 30년 노하우의 전통 분식을 매일 새로 만들어 드립니다. 시장 다녀가는 길 꼭 들러보세요.",
    ],
}

def gen_stories(stores: list, merchants: list) -> list:
    out = []
    counter = 1
    merchant_map = {m["store_id"]: m for m in merchants}
    today = datetime(2026, 5, 10, 9, 0, 0)
    for s in stores:
        n_story = random.randint(1, 3)
        profile = s.get("_profile", "misc")
        templates = STORY_TEMPLATES_BY_PROFILE.get(profile, STORY_TEMPLATES_BY_PROFILE["misc"])
        for k in range(n_story):
            tpl = random.choice(templates)
            content = tpl.format(store=s["store_name"])
            short = content[:50] + "..." if len(content) > 50 else content
            normal = content
            detailed = content + " 오늘도 제철 재료와 점포만의 기준으로 장보기 경험을 더 좋게 만들겠습니다."
            sel = random.choice(["short", "normal", "detailed"])
            chosen = {"short": short, "normal": normal, "detailed": detailed}[sel]
            tone = random.choice(STORY_TONES)
            hashtags = [f"#{s['store_name'].replace(' ', '')}", f"#{CATEGORY_BY_PROFILE.get(profile, '시장')}", "#망원시장" if "망원" in s["store_name"] else "#전통시장"]
            is_pub = random.choices([0, 1], weights=[40, 60])[0]
            published_at = (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S") if is_pub else None
            created_at = (today - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d %H:%M:%S")
            out.append({
                "story_id":         f"st{counter:06d}-e5f6-4789-a012-b3c4d5e6f7{counter % 100:02d}",
                "store_id":         s["store_id"],
                "merchant_id":      (merchant_map.get(s["store_id"]) or {}).get("merchant_id"),
                "title":            None,
                "content":          chosen,
                "content_short":    short,
                "content_normal":   normal,
                "content_detailed": detailed,
                "tone":             tone,
                "selected_length":  sel,
                "hashtags_json":    json.dumps(hashtags, ensure_ascii=False),
                "interview_text":   None,
                "fallback_mode":    0,
                "is_published":     is_pub,
                "published_at":     published_at,
                "created_at":       created_at,
            })
            counter += 1
    return out


# ─────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== mock_v2 생성 ===")
    print(f"입력: {SRC_DIR}")
    print(f"출력: {DST_DIR}")
    print()

    markets_in   = load("markets.json")
    users_in     = load("users.json")
    stores_in    = load("stores.json")
    merchants_in = load("merchants.json")
    products_in  = load("products.json")
    drops_in     = load("drop_events.json")
    catalog_in   = load("catalog_items.json")
    sl_in        = load("shopping_lists.json")
    sli_in       = load("shopping_list_items.json")
    rp_in        = load("route_plans.json")
    nt_in        = load("notifications.json")
    po_in        = load("preorders.json")

    markets   = expand_markets(markets_in)
    users     = expand_users(users_in)
    stores    = expand_stores(stores_in, markets)
    merchants = expand_merchants(merchants_in, stores, users)
    products  = expand_products(products_in, stores)
    drops     = expand_drops(drops_in, products)
    catalog   = expand_catalog_items(catalog_in, markets, stores, products, drops)
    sl, sli   = expand_shopping_lists(sl_in, sli_in, users, products)
    rp        = expand_route_plans(rp_in, users, markets, stores)
    nt        = expand_notifications(nt_in, users, drops, products, catalog)
    po        = expand_preorders(po_in, users, products)

    market_prices    = gen_market_prices()
    price_histories  = gen_price_histories(products, market_prices)
    stories          = gen_stories(stores, merchants)

    # Store JSON 출력 시 임시 _profile/_products 제거
    stores_out = [{k: v for k, v in s.items() if not k.startswith("_")} for s in stores]

    dump("markets.json",                 markets)
    dump("users.json",                   users)
    dump("stores.json",                  stores_out)
    dump("merchants.json",               merchants)
    dump("products.json",                products)
    dump("drop_events.json",             drops)
    dump("catalog_items.json",           catalog)
    dump("shopping_lists.json",          sl)
    dump("shopping_list_items.json",     sli)
    dump("route_plans.json",             rp)
    dump("notifications.json",           nt)
    dump("preorders.json",               po)
    dump("market_prices.json",           market_prices)
    dump("product_price_histories.json", price_histories)
    dump("stories.json",                 stories)

    print()
    print("✅ mock_v2 생성 완료")


if __name__ == "__main__":
    main()
