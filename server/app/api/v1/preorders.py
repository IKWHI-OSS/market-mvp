"""
Preorder API
  POST   /preorders                               — 사전 주문 생성 (consumer/merchant)
  GET    /preorders                               — 내 사전 주문 목록 (?status= 필터)
  GET    /preorders/{preorder_id}                 — 단건 조회
  DELETE /preorders/{preorder_id}                 — 소비자 직접 취소 (requested만)
  PATCH  /merchant/preorders/{preorder_id}/status — 상태 변경 (merchant)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import preorder_service
from app.services.auth_service import get_current_user

router = APIRouter(tags=["preorders"])


# ── 소비자/공통 ──────────────────────────────────────────────────────

class PreorderCreate(BaseModel):
    store_id:     str
    product_name: str
    qty:          int = Field(..., ge=1)


@router.post("/preorders", response_model=BaseResponse)
def create_preorder(
    req: PreorderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """사전 주문 생성 — 소비자·상인 모두 가능."""
    data = preorder_service.create_preorder(
        db,
        current_user,
        store_id=req.store_id,
        product_name=req.product_name,
        qty=req.qty,
    )
    return success_response(data)


@router.get("/preorders", response_model=BaseResponse)
def list_preorders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="상태 필터: requested|confirmed|ready|cancelled"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    내 사전 주문 목록.
    - consumer: 본인 주문만 조회
    - merchant: 담당 점포 주문 전체 조회
    - ?status= 로 상태 필터링 가능
    """
    data = preorder_service.list_preorders(db, current_user, page, size, status)
    return success_response(data)


@router.get("/preorders/{preorder_id}", response_model=BaseResponse)
def get_preorder(
    preorder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    단건 조회.
    - consumer: 본인 주문만 조회 가능
    - merchant: 담당 점포 주문만 조회 가능
    - 권한 외 접근 시 403
    """
    data = preorder_service.get_preorder(db, current_user, preorder_id)
    return success_response(data)


@router.delete("/preorders/{preorder_id}", response_model=BaseResponse)
def cancel_preorder(
    preorder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    소비자 직접 취소.
    - consumer 전용
    - requested 상태일 때만 가능 (그 외 → 409)
    - 취소 시 Notification 자동 생성
    """
    data = preorder_service.cancel_preorder(db, current_user, preorder_id)
    return success_response(data)


# ── 상인 전용 ────────────────────────────────────────────────────────

class PreorderStatusUpdate(BaseModel):
    status: str


@router.patch("/merchant/preorders/{preorder_id}/status", response_model=BaseResponse)
def update_preorder_status(
    preorder_id: str,
    req: PreorderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preorder 상태 변경 (merchant 전용).
    상태 변경 시 주문자에게 Notification 자동 생성.

    허용 전이:
      requested → confirmed | cancelled
      confirmed → ready     | cancelled
      ready     → cancelled
    """
    data = preorder_service.update_status(
        db, current_user, preorder_id, req.status
    )
    return success_response(data)
