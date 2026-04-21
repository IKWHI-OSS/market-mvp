from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest
from app.schemas.common import BaseResponse, success_response
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=BaseResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    data = auth_service.login(req.email, req.password, db)
    return success_response(data)


@router.get("/me", response_model=BaseResponse)
def me(current_user: User = Depends(auth_service.get_current_user)):
    return success_response({
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role.value,
        "name": current_user.name,
    })
