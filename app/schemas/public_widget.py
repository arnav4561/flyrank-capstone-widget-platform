from uuid import UUID

from pydantic import BaseModel


class PublicWidgetResponse(BaseModel):
    public_id: UUID
    type: str
    title: str
    description: str | None
    fields: list
    button_text: str
    display_options: dict
    version: int