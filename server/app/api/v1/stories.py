"""
상인 스토리 API (SPEC.md ADR-04)

  POST   /merchant/stories                  — LLM 스토리 생성 + 저장 (선택 게시)
  GET    /merchant/stories                  — 본인 점포 스토리 목록
  GET    /merchant/stories/{story_id}       — 상세
  PATCH  /merchant/stories/{story_id}       — 길이/제목 수정
  PATCH  /merchant/stories/{story_id}/publish — 게시 토글
  DELETE /merchant/stories/{story_id}       — 소프트 삭제
  GET    /stores/{store_id}/story           — 소비자용: 게시된 최신 스토리
"""
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.services import story_service
from app.services.auth_service import get_current_user

router = APIRouter(tags=["stories"])


class StoryRequest(BaseModel):
    store_id: Optional[str] = None
    save_to_store: Optional[bool] = False
    interview_text: Optional[str] = None
    keywords: Optional[list[str]] = None
    tone: Optional[Literal["친근한", "전문적인", "정겨운"]] = "친근한"
    selected_length: Optional[Literal["short", "normal", "detailed"]] = "normal"
    publish: Optional[bool] = False
    persist: Optional[bool] = True


class StoryUpdateRequest(BaseModel):
    selected_length: Optional[Literal["short", "normal", "detailed"]] = None
    title: Optional[str] = None


class StoryPublishRequest(BaseModel):
    publish: bool


@router.post("/merchant/stories", response_model=BaseResponse)
def create_story(
    req: StoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """LLM(또는 fallback)으로 스토리 생성 → Story 테이블 저장."""
    data = story_service.generate_story(
        db,
        current_user,
        req.store_id,
        save_to_store=req.save_to_store or False,
        interview_text=req.interview_text,
        keywords=req.keywords,
        tone=req.tone or "친근한",
        selected_length=req.selected_length or "normal",
        publish=req.publish or False,
        persist=True if req.persist is None else bool(req.persist),
    )
    return success_response(data)


@router.get("/merchant/stories", response_model=BaseResponse)
def list_my_stories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = story_service.list_stories_for_merchant(db, current_user)
    return success_response({"items": items})


@router.get("/merchant/stories/{story_id}", response_model=BaseResponse)
def get_my_story(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return success_response(story_service.get_story(db, story_id))


@router.patch("/merchant/stories/{story_id}", response_model=BaseResponse)
def patch_story(
    story_id: str,
    req: StoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return success_response(
        story_service.update_story(
            db, current_user, story_id,
            selected_length=req.selected_length,
            title=req.title,
        )
    )


@router.patch("/merchant/stories/{story_id}/publish", response_model=BaseResponse)
def patch_publish(
    story_id: str,
    req: StoryPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return success_response(
        story_service.set_publish(db, current_user, story_id, req.publish)
    )


@router.delete("/merchant/stories/{story_id}", response_model=BaseResponse)
def delete_my_story(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return success_response(story_service.delete_story(db, current_user, story_id))


@router.get("/stores/{store_id}/story", response_model=BaseResponse)
def get_published_store_story(
    store_id: str,
    db: Session = Depends(get_db),
):
    """소비자용 — 점포에 게시된 최신 스토리. 없으면 null 반환."""
    data = story_service.get_published_story_for_store(db, store_id)
    return success_response(data or {})
