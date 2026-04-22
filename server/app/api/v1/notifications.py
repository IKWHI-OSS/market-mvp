from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import notification_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=BaseResponse)
def list_notifications(
    is_read: Optional[int] = Query(None, ge=0, le=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_read_bool = bool(is_read) if is_read is not None else None
    data = notification_service.get_notifications(db, current_user.user_id, is_read_bool, page, size)
    return success_response(data)


@router.patch("/{notification_id}/read", response_model=BaseResponse)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = notification_service.read_notification(db, notification_id, current_user.user_id)
    return success_response(data)
