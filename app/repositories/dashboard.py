from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.models.widget import Widget


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_widgets(
        self,
        tenant_id: UUID,
    ) -> list[Widget]:
        statement = (
            select(Widget)
            .where(Widget.tenant_id == tenant_id)
            .order_by(Widget.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def list_submissions(
        self,
        tenant_id: UUID,
        widget_id: UUID,
    ) -> list[Submission]:
        statement = (
            select(Submission)
            .where(
                Submission.tenant_id == tenant_id,
                Submission.widget_id == widget_id,
            )
            .order_by(Submission.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_submission_count(
        self,
        tenant_id: UUID,
        widget_id: UUID,
    ) -> int:
        statement = select(func.count(Submission.id)).where(
            Submission.tenant_id == tenant_id,
            Submission.widget_id == widget_id,
        )

        return int(self.db.scalar(statement) or 0)

    def get_latest_submission(
        self,
        tenant_id: UUID,
        widget_id: UUID,
    ) -> Submission | None:
        statement = (
            select(Submission)
            .where(
                Submission.tenant_id == tenant_id,
                Submission.widget_id == widget_id,
            )
            .order_by(Submission.created_at.desc())
            .limit(1)
        )

        return self.db.scalar(statement)