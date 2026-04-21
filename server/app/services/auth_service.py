from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token, verify_password
from app.db.models.user import User
from app.db.repositories.user_repository import get_user_by_email, get_user_by_id
from app.db.session import get_db

_bearer = HTTPBearer()

_HOME_SCREEN = {
    "consumer": "SCR-C-01",
    "merchant": "SCR-M-01",
    "operator": "SCR-C-01",
}


def login(email: str, password: str, db: Session) -> dict:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    token = create_access_token({"user_id": user.user_id, "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
        },
        "home_screen_id": _HOME_SCREEN.get(user.role.value, "SCR-C-01"),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload["user_id"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user
