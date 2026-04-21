from fastapi import APIRouter

from app.api.v1 import auth, home, products

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(home.router)
router.include_router(products.router)
