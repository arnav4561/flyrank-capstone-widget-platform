from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.tenant import get_current_tenant
from app.core.database import get_db
from app.models.tenant import Tenant
from app.repositories.widget import WidgetRepository
from app.schemas.widget import WidgetCreate, WidgetResponse, WidgetUpdate
from app.services.widget import WidgetService

router = APIRouter(
    prefix="/api/v1/widgets",
    tags=["widgets"],
)


def get_widget_service(
    db: Session = Depends(get_db),
) -> WidgetService:
    repository = WidgetRepository(db)
    return WidgetService(repository)


@router.post(
    "",
    response_model=WidgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_widget(
    data: WidgetCreate,
    tenant: Tenant = Depends(get_current_tenant),
    service: WidgetService = Depends(get_widget_service),
):
    return service.create_widget(tenant.id, data)


@router.get(
    "",
    response_model=list[WidgetResponse],
)
def list_widgets(
    tenant: Tenant = Depends(get_current_tenant),
    service: WidgetService = Depends(get_widget_service),
):
    return service.list_widgets(tenant.id)


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def get_widget(
    widget_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: WidgetService = Depends(get_widget_service),
):
    widget = service.get_widget(widget_id, tenant.id)

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return widget


@router.patch(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def update_widget(
    widget_id: UUID,
    data: WidgetUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    service: WidgetService = Depends(get_widget_service),
):
    widget = service.get_widget(widget_id, tenant.id)

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return service.update_widget(widget, data)


@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_widget(
    widget_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: WidgetService = Depends(get_widget_service),
):
    widget = service.get_widget(widget_id, tenant.id)

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    service.delete_widget(widget)