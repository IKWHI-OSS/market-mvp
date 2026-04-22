from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import catalog_service

router = APIRouter(tags=["events"])


@router.get("/events/{catalog_item_id}", response_model=BaseResponse)
def get_event(catalog_item_id: str, db: Session = Depends(get_db)):
    data = catalog_service.get_event(db, catalog_item_id)
    return success_response(data)
