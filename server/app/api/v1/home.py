from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import home_service

router = APIRouter(tags=["home"])


@router.get("/home", response_model=BaseResponse)
def get_home(
    market_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = home_service.get_home_feed(db, market_id)
    return success_response(data)
