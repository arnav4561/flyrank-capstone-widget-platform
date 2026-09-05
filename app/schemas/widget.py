from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WidgetCreate(BaseModel):
    type: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    fields: list = Field(default_factory=list)
    button_text: str = Field(
        default="Submit",
        min_length=1,
        max_length=100,
    )
    display_options: dict = Field(default_factory=dict)


class WidgetUpdate(BaseModel):
    type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    fields: list | None = None
    button_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    display_options: dict | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_id: UUID
    tenant_id: UUID
    type: str
    title: str
    description: str | None
    fields: list
    button_text: str
    display_options: dict
    version: int