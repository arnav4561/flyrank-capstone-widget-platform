from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limit import check_rate_limit
from app.repositories.submission import SubmissionRepository
from app.repositories.widget import WidgetRepository
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.geo import GeoService
from app.services.submission import SubmissionService


router = APIRouter(
    prefix="/api/v1/public/widgets",
    tags=["public-submissions"],
)

MAX_PAYLOAD_BYTES = 16_384
MAX_IDEMPOTENCY_KEY_LENGTH = 255


def get_submission_service(
    db: Session = Depends(get_db),
) -> SubmissionService:
    repository = SubmissionRepository(db)
    return SubmissionService(repository)


def validate_submission_fields(
    widget_fields: list,
    submitted_data: dict,
) -> None:
    if not isinstance(widget_fields, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid widget field configuration",
        )

    allowed_names: set[str] = set()

    for field in widget_fields:
        if not isinstance(field, dict):
            continue

        name = field.get("name")

        if not isinstance(name, str) or not name:
            continue

        allowed_names.add(name)

        if field.get("required") and name not in submitted_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Missing required field: {name}",
            )

        if name in submitted_data:
            value = submitted_data[name]
            field_type = field.get("type")

            if field_type == "email":
                if not isinstance(value, str) or "@" not in value:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Invalid email field: {name}",
                    )

            elif field_type == "text":
                if not isinstance(value, str):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Invalid text field: {name}",
                    )

    unexpected_fields = set(submitted_data) - allowed_names

    if unexpected_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unexpected submission field",
        )


def build_response(submission):
    return {
        "id": str(submission.id),
        "widget_id": str(submission.widget_id),
        "country": submission.country,
        "city": submission.city,
        "created_at": submission.created_at.isoformat(),
    }


async def parse_submission_payload(
    request: Request,
) -> SubmissionCreate:
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            declared_length = int(content_length)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Content-Length",
            )

        if declared_length > MAX_PAYLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request payload too large",
            )

    body = await request.body()

    if len(body) > MAX_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Request payload too large",
        )

    try:
        return SubmissionCreate.model_validate_json(body)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid submission payload",
        )


@router.post(
    "/{public_id}/submissions",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_submission(
    public_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    service: SubmissionService = Depends(get_submission_service),
):
    payload = await parse_submission_payload(request)

    widget_repository = WidgetRepository(db)

    widget = widget_repository.get_by_public_id(public_id)

    if widget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    client_ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submissions. Please try again later.",
        )

    if payload.honeypot.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission",
        )

    validate_submission_fields(
        widget_fields=widget.fields,
        submitted_data=payload.data,
    )

    idempotency_key = request.headers.get("Idempotency-Key")

    if idempotency_key:
        idempotency_key = idempotency_key.strip()

        if not idempotency_key:
            idempotency_key = None

        elif len(idempotency_key) > MAX_IDEMPOTENCY_KEY_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idempotency-Key is too long",
            )

    if idempotency_key:
        existing = service.get_existing_submission(
            tenant_id=widget.tenant_id,
            widget_id=widget.id,
            idempotency_key=idempotency_key,
        )

        if existing is not None:
            return build_response(existing)

    user_agent = request.headers.get("user-agent")
    source_origin = request.headers.get("origin")

    geo_service = GeoService()
    geo = geo_service.lookup(client_ip)

    submission = service.create_submission(
        tenant_id=widget.tenant_id,
        widget_id=widget.id,
        data=payload.data,
        ip_address=client_ip,
        country=geo["country"],
        city=geo["city"],
        user_agent=user_agent,
        source_origin=source_origin,
        idempotency_key=idempotency_key,
    )

    await service.trigger_side_effects(submission)

    return build_response(submission)