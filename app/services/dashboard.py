from uuid import UUID

from app.models.submission import Submission
from app.models.widget import Widget
from app.repositories.dashboard import DashboardRepository


class DashboardService:
    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    def list_widgets(
        self,
        tenant_id: UUID,
    ) -> list[Widget]:
        return self.repository.list_widgets(tenant_id)

    def list_submissions(
        self,
        tenant_id: UUID,
        widget_id: UUID,
    ) -> list[Submission]:
        return self.repository.list_submissions(
            tenant_id=tenant_id,
            widget_id=widget_id,
        )

    def get_stats(
        self,
        tenant_id: UUID,
        widget_id: UUID,
    ) -> tuple[int, Submission | None]:
        count = self.repository.get_submission_count(
            tenant_id=tenant_id,
            widget_id=widget_id,
        )

        latest = self.repository.get_latest_submission(
            tenant_id=tenant_id,
            widget_id=widget_id,
        )

        return count, latest