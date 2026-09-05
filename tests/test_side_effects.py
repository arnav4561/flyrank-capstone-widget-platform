import pytest

from app.services.submission import SubmissionService


class FakeRepository:
    pass


class FakeSubmission:
    id = "test-submission-id"

    data = {
        "email": "test@example.com",
    }


@pytest.mark.anyio
async def test_side_effect_failure_does_not_raise(monkeypatch):
    service = SubmissionService(FakeRepository())

    async def failing_send_submission_event(submission_id, email):
        raise RuntimeError("Simulated event queue failure")

    monkeypatch.setattr(
        "app.services.submission.send_submission_event",
        failing_send_submission_event,
    )

    # The service should catch the failure and not break the submission flow.
    await service.trigger_side_effects(FakeSubmission())