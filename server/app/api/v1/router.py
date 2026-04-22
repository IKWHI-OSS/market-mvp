from fastapi import APIRouter

from app.api.v1 import auth, drops, events, home, notifications, products, shopping_lists, stores

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(home.router)
router.include_router(products.router)
router.include_router(events.router)
router.include_router(stores.router)
router.include_router(drops.router)
router.include_router(notifications.router)
router.include_router(shopping_lists.router)
