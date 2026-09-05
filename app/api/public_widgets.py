from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.widget import WidgetRepository
from app.schemas.public_widget import PublicWidgetResponse
from app.services.widget import WidgetService

router = APIRouter(
    prefix="/api/v1/public/widgets",
    tags=["public-widgets"],
)


def get_public_widget_service(
    db: Session = Depends(get_db),
) -> WidgetService:
    repository = WidgetRepository(db)
    return WidgetService(repository)


@router.get(
    "/{public_id}",
    response_model=PublicWidgetResponse,
)
def get_public_widget(
    public_id: UUID,
    response: Response,
    service: WidgetService = Depends(get_public_widget_service),
):
    widget = service.get_public_widget(public_id)

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    response.headers["Cache-Control"] = "public, max-age=60"

    return widget