import inngest

from app.core.inngest import inngest_client


@inngest_client.create_function(
    fn_id="process-submission-side-effects",
    trigger=inngest.TriggerEvent(
        event="widget/submission.created",
    ),
    retries=3,
)
async def process_submission_side_effects(ctx: inngest.Context):
    submission_id = ctx.event.data.get("submission_id")
    email = ctx.event.data.get("email")

    try:
        # Placeholder for the real email/webhook side effect.
        #
        # This intentionally raises when requested so that
        # retry/failure behavior can be demonstrated locally.
        if ctx.event.data.get("simulate_failure"):
            raise RuntimeError("Simulated side-effect failure")

        print(
            f"[SIDE EFFECT] Submission {submission_id} "
            f"processed for {email or 'unknown recipient'}"
        )

    except Exception as exc:
        print(
            f"[SIDE EFFECT ALERT] Submission {submission_id} "
            f"failed after retry handling: {exc}"
        )
        raise