from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import route_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/routes", tags=["routes"])


class RoutePlanCreate(BaseModel):
    market_id: str
    shopping_list_id: str


@router.post("/plans", response_model=BaseResponse)
def create_route_plan(
    req: RoutePlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = route_service.create_route_plan(db, current_user.user_id, req.market_id, req.shopping_list_id)
    return success_response(data)


@router.get("/plans/{route_plan_id}", response_model=BaseResponse)
def get_route_plan(
    route_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = route_service.get_route_plan(db, route_plan_id, current_user.user_id)
    return success_response(data)
