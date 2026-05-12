"""
Story — 상인 스토리 LLM 생성 결과 저장 (SPEC.md ADR-04)
"""
import enum
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer,
    Enum as SAEnum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class StoryLengthEnum(str, enum.Enum):
    short    = "short"
    normal   = "normal"
    detailed = "detailed"


class Story(Base):
    __tablename__ = "Story"

    story_id          = Column(String(36), primary_key=True)
    store_id          = Column(String(36), ForeignKey("Store.store_id"), nullable=False)
    merchant_id       = Column(String(36), nullable=True)
    title             = Column(String(200), nullable=True)
    content           = Column(Text, nullable=False)
    content_short     = Column(Text, nullable=True)
    content_normal    = Column(Text, nullable=True)
    content_detailed  = Column(Text, nullable=True)
    tone              = Column(String(50), nullable=True, default="친근한")
    selected_length   = Column(SAEnum(StoryLengthEnum), nullable=False,
                               default=StoryLengthEnum.normal)
    hashtags_json     = Column(Text, nullable=True)
    interview_text    = Column(Text, nullable=True)
    fallback_mode     = Column(Integer, nullable=False, default=0)
    is_published      = Column(Integer, nullable=False, default=0)
    published_at      = Column(DateTime, nullable=True)
    deleted_at        = Column(DateTime, nullable=True)
    updated_at        = Column(DateTime, onupdate=func.now())
    created_at        = Column(DateTime, server_default=func.now())

    store = relationship("Store", backref="stories")
