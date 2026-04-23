from fastapi import APIRouter

from app.api.v1 import (
    auth, drops, events, home, merchant, notifications,
    products, routes, shopping_lists, stores,
    prices, stories, preorders, shopping_agent,
)

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(home.router)
router.include_router(products.router)
router.include_router(events.router)
router.include_router(stores.router)
router.include_router(drops.router)
router.include_router(notifications.router)
router.include_router(shopping_lists.router)
router.include_router(merchant.router)
router.include_router(routes.router)
router.include_router(prices.router)
router.include_router(stories.router)
router.include_router(preorders.router)
router.include_router(shopping_agent.router)
