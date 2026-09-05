from uuid import UUID

from app.core.inngest import send_submission_event
from app.models.submission import Submission
from app.repositories.submission import SubmissionRepository


class SubmissionService:
    def __init__(self, repository: SubmissionRepository):
        self.repository = repository

    def create_submission(
        self,
        tenant_id: UUID,
        widget_id: UUID,
        data: dict,
        ip_address: str | None,
        country: str | None,
        city: str | None,
        user_agent: str | None,
        source_origin: str | None,
        idempotency_key: str | None,
    ) -> Submission:
        return self.repository.create(
            tenant_id=tenant_id,
            widget_id=widget_id,
            data=data,
            ip_address=ip_address,
            country=country,
            city=city,
            user_agent=user_agent,
            source_origin=source_origin,
            idempotency_key=idempotency_key,
        )

    def get_existing_submission(
        self,
        tenant_id: UUID,
        widget_id: UUID,
        idempotency_key: str,
    ) -> Submission | None:
        return self.repository.get_by_idempotency_key(
            tenant_id=tenant_id,
            widget_id=widget_id,
            idempotency_key=idempotency_key,
        )

    async def trigger_side_effects(
        self,
        submission: Submission,
    ) -> None:
        email = submission.data.get("email")

        try:
            await send_submission_event(
                submission_id=str(submission.id),
                email=email if isinstance(email, str) else None,
            )
        except Exception as exc:
            # Side effects are non-critical.
            # A failure here must never fail the submission.
            print(
                f"[SIDE EFFECT ALERT] "
                f"Could not queue side effects for "
                f"submission {submission.id}: {exc}"
            )