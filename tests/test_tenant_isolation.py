from uuid import uuid4

from app.repositories.widget import WidgetRepository
from app.services.widget import WidgetService


class FakeWidget:
    def __init__(self, widget_id, tenant_id):
        self.id = widget_id
        self.tenant_id = tenant_id


class FakeWidgetRepository:
    def __init__(self, widgets):
        self.widgets = widgets

    def get_by_id(self, widget_id, tenant_id):
        for widget in self.widgets:
            if widget.id == widget_id and widget.tenant_id == tenant_id:
                return widget
        return None


def test_tenant_cannot_access_another_tenant_widget():
    tenant_a = uuid4()
    tenant_b = uuid4()
    widget_a = FakeWidget(uuid4(), tenant_a)

    repository = FakeWidgetRepository([widget_a])
    service = WidgetService(repository)

    result = service.get_widget(widget_a.id, tenant_b)

    assert result is None


def test_tenant_can_access_own_widget():
    tenant_a = uuid4()
    widget_a = FakeWidget(uuid4(), tenant_a)

    repository = FakeWidgetRepository([widget_a])
    service = WidgetService(repository)

    result = service.get_widget(widget_a.id, tenant_a)

    assert result is widget_a