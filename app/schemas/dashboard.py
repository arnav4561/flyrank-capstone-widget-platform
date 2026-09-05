from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DashboardWidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_id: UUID
    type: str
    title: str
    version: int
    created_at: datetime
    updated_at: datetime


class DashboardSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    widget_id: UUID
    data: dict
    country: str | None
    city: str | None
    source_origin: str | None
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    widget_id: UUID
    total_submissions: int
    latest_submission_at: datetime | None