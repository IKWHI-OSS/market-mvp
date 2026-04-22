from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.repositories import route_repository as repo


def _build_route_json(items_with_stores: list) -> dict:
    store_steps = {}  # store_id → {store_id, store_name, zone_label, items: []}
    no_store_items = []

    for item, store in items_with_stores:
        if store:
            sid = store.store_id
            if sid not in store_steps:
                store_steps[sid] = {
                    "store_id": store.store_id,
                    "store_name": store.store_name,
                    "zone_label": store.zone_label,
                    "items": [],
                }
            store_steps[sid]["items"].append(item.product_name_snapshot)
        else:
            no_store_items.append(item.product_name_snapshot)

    # Sort store steps: zone_label alphabetically, None last
    sorted_store_steps = sorted(
        store_steps.values(),
        key=lambda s: (s["zone_label"] is None, s["zone_label"] or ""),
    )

    steps = list(sorted_store_steps)
    if no_store_items:
        steps.append({"store_id": None, "store_name": None, "zone_label": None, "items": no_store_items})

    return {"steps": steps}


def _build_navigation_guide(route_json: dict) -> str:
    steps = route_json.get("steps", [])
    zones = [s["zone_label"] for s in steps if s.get("zone_label")]
    if not zones:
        return "동선 정보가 없습니다."
    return " → ".join(zones) + " 순서로 이동하세요."


def _plan_out(plan, route_json=None) -> dict:
    rj = route_json if route_json is not None else plan.route_json
    return {
        "route_plan_id": plan.route_plan_id,
        "market_id": plan.market_id,
        "shopping_list_id": plan.shopping_list_id,
        "route_json": rj,
        "navigation_guide": _build_navigation_guide(rj),
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }


def create_route_plan(db: Session, user_id: str, market_id: str, shopping_list_id: str) -> dict:
    sl = repo.get_shopping_list(db, shopping_list_id, user_id)
    if not sl:
        raise HTTPException(status_code=404, detail="장보기 리스트를 찾을 수 없습니다.")
    market = repo.get_market(db, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="시장을 찾을 수 없습니다.")

    items_with_stores = repo.get_items_with_stores(db, shopping_list_id)
    route_json = _build_route_json(items_with_stores)
    plan = repo.create_route_plan(db, user_id, market_id, shopping_list_id, route_json)
    return _plan_out(plan, route_json)


def get_route_plan(db: Session, route_plan_id: str, user_id: str) -> dict:
    plan = repo.get_route_plan(db, route_plan_id, user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="동선을 찾을 수 없습니다.")
    return _plan_out(plan)
