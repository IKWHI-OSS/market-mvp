from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import shopping_agent_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/shopping-agent", tags=["shopping-agent"])


class ShoppingAgentRequest(BaseModel):
    query: str = Field(..., min_length=1, description="자연어 장보기 질의")
    people: Optional[int] = Field(default=None, ge=1, le=10)
    budget: Optional[int] = Field(default=None, ge=1000)
    preferences: Optional[list[str]] = None
    market_id: Optional[str] = None
    save_as_list: bool = True


@router.post("/recommendations", response_model=BaseResponse)
def create_recommendation(
    req: ShoppingAgentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_agent_service.generate_agent_recommendation(
        db=db,
        user_id=current_user.user_id,
        query=req.query,
        people=req.people,
        budget=req.budget,
        preferences=req.preferences,
        market_id=req.market_id,
        save_as_list=req.save_as_list,
    )
    return success_response(data)
