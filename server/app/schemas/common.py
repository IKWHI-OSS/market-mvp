import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel


class Meta(BaseModel):
    request_id: str
    timestamp: str


class BaseResponse(BaseModel):
    success: bool = True
    code: str = "OK"
    message: str = "요청이 성공했습니다."
    data: Any = None
    meta: Optional[Meta] = None


def success_response(data: Any, message: str = "요청이 성공했습니다.") -> BaseResponse:
    return BaseResponse(
        data=data,
        message=message,
        meta=Meta(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )
