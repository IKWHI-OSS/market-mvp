# server/app/core/config.py
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL_STORY: str = "claude-3-5-haiku-latest"
    ANTHROPIC_MODEL_SHOPPING_AGENT: str = "claude-3-5-haiku-latest"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
