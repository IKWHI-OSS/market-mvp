"""
story_repository — Story 테이블 CRUD
"""
import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.story import Story, StoryLengthEnum


def create_story(
    db: Session,
    *,
    store_id: str,
    merchant_id: Optional[str],
    content: str,
    versions: dict,
    tone: str,
    selected_length: str,
    hashtags: list[str],
    interview_text: Optional[str],
    fallback_mode: bool,
    title: Optional[str] = None,
    is_published: bool = False,
) -> Story:
    length_enum = StoryLengthEnum(selected_length) if selected_length in [
        e.value for e in StoryLengthEnum
    ] else StoryLengthEnum.normal

    s = Story(
        story_id          = str(uuid.uuid4()),
        store_id          = store_id,
        merchant_id       = merchant_id,
        title             = title,
        content           = content,
        content_short     = versions.get("short"),
        content_normal    = versions.get("normal"),
        content_detailed  = versions.get("detailed"),
        tone              = tone,
        selected_length   = length_enum,
        hashtags_json     = json.dumps(hashtags, ensure_ascii=False),
        interview_text    = interview_text,
        fallback_mode     = 1 if fallback_mode else 0,
        is_published      = 1 if is_published else 0,
        published_at      = datetime.utcnow() if is_published else None,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_by_id(db: Session, story_id: str) -> Optional[Story]:
    return (
        db.query(Story)
        .filter(Story.story_id == story_id, Story.deleted_at.is_(None))
        .first()
    )


def list_by_store(
    db: Session, store_id: str, only_published: bool = False, limit: int = 50
) -> list[Story]:
    q = db.query(Story).filter(
        Story.store_id == store_id,
        Story.deleted_at.is_(None),
    )
    if only_published:
        q = q.filter(Story.is_published == 1)
    return q.order_by(Story.created_at.desc()).limit(limit).all()


def list_by_merchant(
    db: Session, merchant_id: str, limit: int = 100
) -> list[Story]:
    return (
        db.query(Story)
        .filter(Story.merchant_id == merchant_id, Story.deleted_at.is_(None))
        .order_by(Story.created_at.desc())
        .limit(limit)
        .all()
    )


def get_latest_published_for_store(
    db: Session, store_id: str
) -> Optional[Story]:
    return (
        db.query(Story)
        .filter(
            Story.store_id == store_id,
            Story.deleted_at.is_(None),
            Story.is_published == 1,
        )
        .order_by(Story.published_at.desc())
        .first()
    )


def update_publish(db: Session, story: Story, publish: bool) -> Story:
    story.is_published = 1 if publish else 0
    story.published_at = datetime.utcnow() if publish else None
    db.commit()
    db.refresh(story)
    return story


def update_content(
    db: Session,
    story: Story,
    *,
    selected_length: Optional[str] = None,
    title: Optional[str] = None,
) -> Story:
    if selected_length and selected_length in [e.value for e in StoryLengthEnum]:
        story.selected_length = StoryLengthEnum(selected_length)
        chosen = {
            "short":    story.content_short,
            "normal":   story.content_normal,
            "detailed": story.content_detailed,
        }.get(selected_length)
        if chosen:
            story.content = chosen
    if title is not None:
        story.title = title
    db.commit()
    db.refresh(story)
    return story


def soft_delete(db: Session, story: Story) -> Story:
    story.deleted_at = datetime.utcnow()
    story.is_published = 0
    db.commit()
    db.refresh(story)
    return story


def to_dict(s: Story) -> dict:
    try:
        hashtags = json.loads(s.hashtags_json) if s.hashtags_json else []
    except (json.JSONDecodeError, TypeError):
        hashtags = []
    versions = {
        "short":    s.content_short,
        "normal":   s.content_normal,
        "detailed": s.content_detailed,
    }
    return {
        "story_id":        s.story_id,
        "store_id":        s.store_id,
        "merchant_id":     s.merchant_id,
        "title":           s.title,
        "content":         s.content,
        "story_versions":  versions,
        "tone":            s.tone,
        "selected_length": s.selected_length.value if s.selected_length else "normal",
        "hashtags":        hashtags,
        "interview_text":  s.interview_text,
        "fallback_mode":   bool(s.fallback_mode),
        "is_published":    bool(s.is_published),
        "published_at":    s.published_at.isoformat() if s.published_at else None,
        "created_at":      s.created_at.isoformat() if s.created_at else None,
        "updated_at":      s.updated_at.isoformat() if s.updated_at else None,
    }
