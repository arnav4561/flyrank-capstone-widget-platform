from uuid import UUID

from app.models.widget import Widget
from app.repositories.widget import WidgetRepository
from app.schemas.widget import WidgetCreate, WidgetUpdate


class WidgetService:
    def __init__(self, repository: WidgetRepository):
        self.repository = repository

    def create_widget(
        self,
        tenant_id: UUID,
        data: WidgetCreate,
    ) -> Widget:
        return self.repository.create(tenant_id, data)

    def list_widgets(
        self,
        tenant_id: UUID,
    ) -> list[Widget]:
        return self.repository.list_by_tenant(tenant_id)

    def get_widget(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> Widget | None:
        return self.repository.get_by_id(widget_id, tenant_id)

    def get_public_widget(
        self,
        public_id: UUID,
    ) -> Widget | None:
        return self.repository.get_by_public_id(public_id)

    def update_widget(
        self,
        widget: Widget,
        data: WidgetUpdate,
    ) -> Widget:
        return self.repository.update(widget, data)

    def delete_widget(
        self,
        widget: Widget,
    ) -> None:
        self.repository.delete(widget)