import os

import inngest
from dotenv import load_dotenv

load_dotenv()

INNGEST_EVENT_KEY = os.getenv("INNGEST_EVENT_KEY", "")

inngest_client = inngest.Inngest(
    app_id="flyrank-widget-platform",
    is_production=False,
)


async def send_submission_event(
    submission_id: str,
    email: str | None,
) -> None:
    await inngest_client.send(
        inngest.Event(
            name="widget/submission.created",
            data={
                "submission_id": submission_id,
                "email": email,
            },
        )
    )