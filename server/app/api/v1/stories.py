"""
상인 스토리 생성 API
  POST /merchant/stories — LLM 기반 스토리 문구 생성
"""
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import story_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/merchant", tags=["stories"])


class StoryRequest(BaseModel):
    store_id: str
    save_to_store: Optional[bool] = False  # True면 Store.store_story_summary 자동 저장


@router.post("/stories", response_model=BaseResponse)
def create_story(
    req: StoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Store + Product 정보 기반으로 상인 스토리 문구를 LLM으로 생성합니다.
    AI 실패 시 fallback 템플릿을 반환합니다.
    """
    data = story_service.generate_story(
        db,
        current_user,
        req.store_id,
        save_to_store=req.save_to_store or False,
    )
    return success_response(data)
