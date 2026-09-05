from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.widget import Widget
from app.schemas.widget import WidgetCreate, WidgetUpdate


class WidgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, tenant_id: UUID, data: WidgetCreate) -> Widget:
        widget = Widget(
            tenant_id=tenant_id,
            type=data.type,
            title=data.title,
            description=data.description,
            fields=data.fields,
            button_text=data.button_text,
            display_options=data.display_options,
        )

        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)

        return widget

    def list_by_tenant(self, tenant_id: UUID) -> list[Widget]:
        statement = (
            select(Widget)
            .where(Widget.tenant_id == tenant_id)
            .order_by(Widget.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> Widget | None:
        statement = select(Widget).where(
            Widget.id == widget_id,
            Widget.tenant_id == tenant_id,
        )

        return self.db.scalar(statement)

    def get_by_public_id(
        self,
        public_id: UUID,
    ) -> Widget | None:
        statement = select(Widget).where(
            Widget.public_id == public_id
        )

        return self.db.scalar(statement)

    def update(
        self,
        widget: Widget,
        data: WidgetUpdate,
    ) -> Widget:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(widget, field, value)

        widget.version += 1

        self.db.commit()
        self.db.refresh(widget)

        return widget

    def delete(self, widget: Widget) -> None:
        self.db.delete(widget)
        self.db.commit()