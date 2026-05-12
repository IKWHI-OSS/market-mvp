from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import merchant_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.get("/dashboard", response_model=BaseResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.get_dashboard(db, current_user)
    return success_response(data)


class ProductCreate(BaseModel):
    store_id: str
    product_name: str
    price: int
    stock_status: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    quality_note: Optional[str] = None


@router.post("/products", response_model=BaseResponse)
def create_product(
    req: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.create_product(
        db, current_user, req.store_id, req.product_name, req.price,
        req.stock_status, req.category, req.image_url, req.quality_note,
    )
    return success_response(data)


class AIDraftRequest(BaseModel):
    store_id: str
    image_url: Optional[str] = None
    voice_text: Optional[str] = None


@router.post("/products/ai-draft", response_model=BaseResponse)
def ai_draft(
    req: AIDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.ai_draft(db, current_user, req.store_id, req.image_url, req.voice_text)
    return success_response(data)


class ProductUpdate(BaseModel):
    price: Optional[int] = None
    stock_status: Optional[str] = None


@router.patch("/products/{product_id}", response_model=BaseResponse)
def update_product(
    product_id: str,
    req: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.update_product(db, current_user, product_id, req.price, req.stock_status)
    return success_response(data)


@router.get("/my-store", response_model=BaseResponse)
def get_my_store(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.get_my_store(db, current_user)
    return success_response(data)


class DropStatusUpdate(BaseModel):
    status: str


@router.patch("/drops/{drop_id}/status", response_model=BaseResponse)
def update_drop_status(
    drop_id: str,
    req: DropStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = merchant_service.update_drop_status(db, current_user, drop_id, req.status)
    return success_response(data)
