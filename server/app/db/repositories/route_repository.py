import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.route_plan import RoutePlan
from app.db.models.shopping_list import ShoppingList
from app.db.models.shopping_list_item import ShoppingListItem
from app.db.models.store import Store
from app.db.models.market import Market


def get_shopping_list(db: Session, shopping_list_id: str, user_id: str) -> Optional[ShoppingList]:
    return (
        db.query(ShoppingList)
        .filter(ShoppingList.shopping_list_id == shopping_list_id, ShoppingList.user_id == user_id)
        .first()
    )


def get_market(db: Session, market_id: str):
    from app.db.models.market import Market
    return db.query(Market).filter(Market.market_id == market_id).first()


def get_items_with_stores(db: Session, shopping_list_id: str):
    return (
        db.query(ShoppingListItem, Store)
        .outerjoin(Store, ShoppingListItem.store_id == Store.store_id)
        .filter(ShoppingListItem.shopping_list_id == shopping_list_id)
        .all()
    )


def create_route_plan(db: Session, user_id: str, market_id: str, shopping_list_id: str,
                      route_json: dict) -> RoutePlan:
    plan = RoutePlan(
        route_plan_id=str(uuid.uuid4()),
        user_id=user_id,
        market_id=market_id,
        shopping_list_id=shopping_list_id,
        route_json=route_json,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_route_plan(db: Session, route_plan_id: str, user_id: str) -> Optional[RoutePlan]:
    return (
        db.query(RoutePlan)
        .filter(RoutePlan.route_plan_id == route_plan_id, RoutePlan.user_id == user_id)
        .first()
    )
