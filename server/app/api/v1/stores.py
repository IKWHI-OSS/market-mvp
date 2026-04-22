from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import catalog_service

router = APIRouter(tags=["stores"])


@router.get("/stores/{store_id}/spotlight", response_model=BaseResponse)
def get_store_spotlight(store_id: str, db: Session = Depends(get_db)):
    data = catalog_service.get_store_spotlight_detail(db, store_id)
    return success_response(data)
