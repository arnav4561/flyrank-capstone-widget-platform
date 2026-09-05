from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.tenant import get_current_tenant
from app.core.database import get_db
from app.models.tenant import Tenant
from app.repositories.dashboard import DashboardRepository
from app.repositories.widget import WidgetRepository
from app.schemas.dashboard import (
    DashboardStatsResponse,
    DashboardSubmissionResponse,
    DashboardWidgetResponse,
)
from app.services.dashboard import DashboardService


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)


def get_dashboard_service(
    db: Session = Depends(get_db),
) -> DashboardService:
    repository = DashboardRepository(db)
    return DashboardService(repository)


@router.get(
    "/widgets",
    response_model=list[DashboardWidgetResponse],
)
def list_dashboard_widgets(
    tenant: Tenant = Depends(get_current_tenant),
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.list_widgets(tenant.id)


@router.get(
    "/widgets/{widget_id}/submissions",
    response_model=list[DashboardSubmissionResponse],
)
def list_dashboard_submissions(
    widget_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: DashboardService = Depends(get_dashboard_service),
):
    widget_repository = WidgetRepository(service.repository.db)

    widget = widget_repository.get_by_id(
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return service.list_submissions(
        tenant_id=tenant.id,
        widget_id=widget_id,
    )


@router.get(
    "/widgets/{widget_id}/stats",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats(
    widget_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: DashboardService = Depends(get_dashboard_service),
):
    widget_repository = WidgetRepository(service.repository.db)

    widget = widget_repository.get_by_id(
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    count, latest = service.get_stats(
        tenant_id=tenant.id,
        widget_id=widget_id,
    )

    return {
        "widget_id": widget_id,
        "total_submissions": count,
        "latest_submission_at": (
            latest.created_at if latest else None
        ),
    }