from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ShortenRequest(BaseModel):
    target_url: HttpUrl
    custom_code: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=8,
        pattern="^[a-zA-Z0-9_-]+$"
    )
    expires_in_seconds: Optional[int] = Field(None, gt=0)

class ShortenResponse(BaseModel):
    code: str
    short_url: HttpUrl
    target_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime]

class StatsResponse(BaseModel):
    code: str
    short_url: HttpUrl
    target_url: HttpUrl
    visit_count: int
    created_at: datetime
    last_accessed_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_expired: bool
