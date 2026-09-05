from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission


class SubmissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
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
        submission = Submission(
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

        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        return submission

    def get_by_idempotency_key(
        self,
        tenant_id: UUID,
        widget_id: UUID,
        idempotency_key: str,
    ) -> Submission | None:
        statement = select(Submission).where(
            Submission.tenant_id == tenant_id,
            Submission.widget_id == widget_id,
            Submission.idempotency_key == idempotency_key,
        )

        return self.db.scalar(statement)

    def list_by_widget(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> list[Submission]:
        statement = (
            select(Submission)
            .where(
                Submission.widget_id == widget_id,
                Submission.tenant_id == tenant_id,
            )
            .order_by(Submission.created_at.desc())
        )

        return list(self.db.scalars(statement).all())