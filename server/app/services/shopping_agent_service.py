"""
shopping_agent_service - SCR-C-05 장보기 에이전트(RAG) MVP

기능:
1) 자연어 질의 -> 메뉴 추천
2) 재료 리스트 생성(대체품 포함)
3) 시장 상품/점포 매칭
4) 필요 시 ShoppingList 자동 생성
"""

from __future__ import annotations

import hashlib
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.product import Product, StockStatusEnum
from app.db.models.store import Store
from app.db.repositories import shopping_list_repository as shopping_repo


_RECIPE_DATASET = [
    {
        "id": "recipe_001",
        "title": "제철 고추장찌개 세트",
        "keywords": ["찌개", "고추장", "저녁", "2인", "국물"],
        "reason": "제철 채소와 단백질 구성이 좋아 한 끼 식사로 균형이 좋습니다.",
        "ingredients": [
            {
                "name": "돼지고기",
                "qty": 300,
                "unit": "g",
                "alternatives": ["소고기", "두부"],
                "seasonal": False,
            },
            {
                "name": "감자",
                "qty": 2,
                "unit": "개",
                "alternatives": ["고구마"],
                "seasonal": True,
            },
            {
                "name": "애호박",
                "qty": 1,
                "unit": "개",
                "alternatives": ["주키니호박"],
                "seasonal": True,
            },
            {
                "name": "대파",
                "qty": 1,
                "unit": "단",
                "alternatives": ["쪽파"],
                "seasonal": True,
            },
        ],
    },
    {
        "id": "recipe_002",
        "title": "봄나물 비빔밥 세트",
        "keywords": ["비빔밥", "봄나물", "건강", "채소", "가벼운"],
        "reason": "가벼운 식사와 제철 나물 소비에 적합한 조합입니다.",
        "ingredients": [
            {
                "name": "시금치",
                "qty": 1,
                "unit": "봉",
                "alternatives": ["청경채"],
                "seasonal": True,
            },
            {
                "name": "콩나물",
                "qty": 1,
                "unit": "봉",
                "alternatives": ["숙주"],
                "seasonal": False,
            },
            {
                "name": "당근",
                "qty": 1,
                "unit": "개",
                "alternatives": ["파프리카"],
                "seasonal": True,
            },
            {
                "name": "계란",
                "qty": 4,
                "unit": "개",
                "alternatives": ["두부"],
                "seasonal": False,
            },
        ],
    },
    {
        "id": "recipe_003",
        "title": "간단 볶음밥 세트",
        "keywords": ["볶음밥", "간단", "자취", "점심", "빠른"],
        "reason": "짧은 조리 시간으로 빠르게 준비 가능한 메뉴입니다.",
        "ingredients": [
            {
                "name": "양파",
                "qty": 1,
                "unit": "개",
                "alternatives": ["대파"],
                "seasonal": False,
            },
            {
                "name": "당근",
                "qty": 1,
                "unit": "개",
                "alternatives": ["브로콜리"],
                "seasonal": True,
            },
            {
                "name": "햄",
                "qty": 1,
                "unit": "팩",
                "alternatives": ["베이컨", "참치"],
                "seasonal": False,
            },
            {
                "name": "계란",
                "qty": 2,
                "unit": "개",
                "alternatives": ["두부"],
                "seasonal": False,
            },
        ],
    },
]


def _is_ambiguous_query(query: str) -> bool:
    q = query.strip()
    if len(q) < 5:
        return True
    generic_tokens = ["추천", "뭐 먹지", "뭐먹지", "메뉴", "음식"]
    return any(t in q for t in generic_tokens) and len(q.split()) <= 2


def _pick_recipe(query: str, preferences: Optional[list[str]]) -> dict[str, Any]:
    q = query.lower()
    pref = " ".join(preferences or []).lower()
    best = None
    best_score = -1
    for recipe in _RECIPE_DATASET:
        score = 0
        for kw in recipe["keywords"]:
            if kw.lower() in q:
                score += 2
            if kw.lower() in pref:
                score += 1
        if score > best_score:
            best = recipe
            best_score = score
    if not best:
        return _RECIPE_DATASET[0]
    return best


def _query_candidates(
    db: Session,
    ingredient_name: str,
    market_id: Optional[str],
) -> list[tuple[Product, Store]]:
    q = (
        db.query(Product, Store)
        .join(Store, Product.store_id == Store.store_id)
        .filter(func.lower(Product.product_name).like(f"%{ingredient_name.lower()}%"))
    )
    if market_id:
        q = q.filter(Store.market_id == market_id)
    return q.order_by(Product.price.asc()).limit(20).all()


def _deterministic_distance(store_id: str, ingredient_name: str) -> int:
    h = hashlib.md5(f"{store_id}:{ingredient_name}".encode("utf-8")).hexdigest()
    return 80 + (int(h[:4], 16) % 420)


def _pick_best_match(
    db: Session,
    ingredient: dict[str, Any],
    market_id: Optional[str],
) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    primary_name = ingredient["name"]
    names = [primary_name] + list(ingredient.get("alternatives") or [])

    for name in names:
        candidates = _query_candidates(db, name, market_id)
        if not candidates:
            continue
        in_stock = [c for c in candidates if c[0].stock_status == StockStatusEnum.in_stock]
        low_stock = [c for c in candidates if c[0].stock_status == StockStatusEnum.low_stock]
        ordered = in_stock + low_stock + candidates
        if not ordered:
            continue
        product, store = ordered[0]
        return (
            {
                "ingredient_name": primary_name,
                "matched_name": product.product_name,
                "product_id": product.product_id,
                "store_id": store.store_id,
                "store_name": store.store_name,
                "zone_label": store.zone_label,
                "price": int(product.price),
                "stock_status": product.stock_status.value,
                "distance_m": _deterministic_distance(store.store_id, primary_name),
            },
            None if name == primary_name else name,
        )
    return None, None


def _fallback_payload(query: str) -> dict[str, Any]:
    return {
        "query": query,
        "clarification_needed": False,
        "clarification_question": None,
        "stage": "menu_list_matching",
        "menu": {
            "title": "기본 장보기 추천 세트",
            "reason": "일시적 오류로 기본 추천 템플릿을 제공합니다.",
            "rag_source": "sample_recipe_dataset_v1",
        },
        "ingredients": [
            {
                "name": "감자",
                "qty": 2,
                "unit": "개",
                "seasonal": True,
                "alternatives": ["고구마"],
                "match_status": "unmatched",
                "matched_store": None,
            },
            {
                "name": "양파",
                "qty": 1,
                "unit": "개",
                "seasonal": False,
                "alternatives": ["대파"],
                "match_status": "unmatched",
                "matched_store": None,
            },
        ],
        "store_matches": [],
        "matching_failed": True,
        "general_list_only": True,
        "shopping_list_id": None,
        "fallback_mode": True,
        "retry_guide": "잠시 후 다시 시도해주세요. 문제가 지속되면 일반 장보기 리스트를 사용해주세요.",
    }


def generate_agent_recommendation(
    db: Session,
    user_id: str,
    query: str,
    people: Optional[int] = None,
    budget: Optional[int] = None,
    preferences: Optional[list[str]] = None,
    market_id: Optional[str] = None,
    save_as_list: bool = True,
) -> dict[str, Any]:
    try:
        clean_query = query.strip()
        if not clean_query:
            raise HTTPException(status_code=422, detail="query는 필수입니다.")

        if _is_ambiguous_query(clean_query):
            return {
                "query": clean_query,
                "clarification_needed": True,
                "clarification_question": "원하시는 식사 유형(찌개/볶음/비빔 등)과 인원/예산을 알려주세요.",
                "stage": "clarification",
                "menu": None,
                "ingredients": [],
                "store_matches": [],
                "matching_failed": False,
                "general_list_only": False,
                "shopping_list_id": None,
                "fallback_mode": False,
                "retry_guide": None,
            }

        recipe = _pick_recipe(clean_query, preferences)
        scale = max(1, int(people or 2))
        if scale > 4:
            scale = 4

        ingredients_out: list[dict[str, Any]] = []
        store_index: dict[str, dict[str, Any]] = {}
        matched_count = 0
        shopping_list_id: Optional[str] = None

        if save_as_list:
            sl = shopping_repo.create_list(
                db,
                user_id,
                f"{recipe['title']} ({scale}인)",
            )
            shopping_list_id = sl.shopping_list_id

        for ing in recipe["ingredients"]:
            scaled_qty = ing["qty"] * scale // 2 if isinstance(ing["qty"], int) else ing["qty"]
            match, substituted = _pick_best_match(db, ing, market_id)

            if match:
                matched_count += 1
                store_entry = store_index.get(match["store_id"])
                if not store_entry:
                    store_entry = {
                        "store_id": match["store_id"],
                        "store_name": match["store_name"],
                        "zone_label": match["zone_label"],
                        "distance_m": match["distance_m"],
                        "matched_items": [],
                        "price_total": 0,
                        "stock_flags": [],
                    }
                    store_index[match["store_id"]] = store_entry
                store_entry["matched_items"].append(ing["name"])
                store_entry["price_total"] += int(match["price"])
                store_entry["stock_flags"].append(match["stock_status"])

                if save_as_list and shopping_list_id:
                    shopping_repo.create_item(
                        db,
                        shopping_list_id,
                        ing["name"],
                        int(scaled_qty),
                        ing["unit"],
                        product_id=match["product_id"],
                        estimated_price=int(match["price"]),
                        store_id=match["store_id"],
                    )

            else:
                if save_as_list and shopping_list_id:
                    shopping_repo.create_item(
                        db,
                        shopping_list_id,
                        ing["name"],
                        int(scaled_qty),
                        ing["unit"],
                        product_id=None,
                        estimated_price=None,
                        store_id=None,
                    )

            ingredients_out.append(
                {
                    "name": ing["name"],
                    "qty": int(scaled_qty),
                    "unit": ing["unit"],
                    "seasonal": bool(ing["seasonal"]),
                    "alternatives": ing.get("alternatives", []),
                    "match_status": "matched" if match else "unmatched",
                    "substituted_with": substituted,
                    "matched_store": None
                    if not match
                    else {
                        "store_id": match["store_id"],
                        "store_name": match["store_name"],
                        "zone_label": match["zone_label"],
                        "price": int(match["price"]),
                        "stock_status": match["stock_status"],
                    },
                }
            )

        store_matches = []
        for store in sorted(store_index.values(), key=lambda x: (x["distance_m"], x["price_total"])):
            stock_priority = "in_stock"
            if any(s == StockStatusEnum.low_stock.value for s in store["stock_flags"]):
                stock_priority = "low_stock"
            if all(s == StockStatusEnum.out_of_stock.value for s in store["stock_flags"]):
                stock_priority = "out_of_stock"
            store_matches.append(
                {
                    "store_id": store["store_id"],
                    "store_name": store["store_name"],
                    "zone_label": store["zone_label"],
                    "distance_m": store["distance_m"],
                    "matched_items": store["matched_items"],
                    "price_total": store["price_total"],
                    "stock_priority": stock_priority,
                }
            )

        matching_failed = matched_count == 0
        return {
            "query": clean_query,
            "clarification_needed": False,
            "clarification_question": None,
            "stage": "menu_list_matching",
            "menu": {
                "title": recipe["title"],
                "reason": recipe["reason"],
                "rag_source": "sample_recipe_dataset_v1",
                "people": scale,
                "budget": budget,
            },
            "ingredients": ingredients_out,
            "store_matches": store_matches,
            "matching_failed": matching_failed,
            "general_list_only": matching_failed,
            "shopping_list_id": shopping_list_id,
            "fallback_mode": False,
            "retry_guide": None if not matching_failed else "점포 매칭이 어려워 일반 장보기 리스트만 먼저 제공했습니다.",
        }
    except HTTPException:
        raise
    except Exception:
        # 일시적 오류 시 기본 추천 템플릿 + 재시도 안내
        return _fallback_payload(query)
