from typing import Any

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
    honeypot: str = Field(default="")


class SubmissionResponse(BaseModel):
    id: str
    widget_id: str
    country: str | None
    city: str | None
    created_at: str
