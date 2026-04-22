from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.common import BaseResponse, success_response
from app.services import drop_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/drops", tags=["drops"])
_bearer = HTTPBearer(auto_error=False)


def _optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return payload.get("user_id")
    except (JWTError, Exception):
        return None


@router.get("", response_model=BaseResponse)
def list_drops(
    market_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Depends(_optional_user_id),
    db: Session = Depends(get_db),
):
    data = drop_service.get_drops(db, market_id, status, page, size, user_id)
    return success_response(data)


@router.post("/{drop_id}/subscribe", response_model=BaseResponse)
def subscribe_drop(
    drop_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = drop_service.subscribe_drop(db, drop_id, current_user.user_id)
    return success_response(data)


@router.delete("/{drop_id}/subscribe", response_model=BaseResponse)
def unsubscribe_drop(
    drop_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = drop_service.unsubscribe_drop(db, drop_id, current_user.user_id)
    return success_response(data)
