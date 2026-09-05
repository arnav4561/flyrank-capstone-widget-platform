from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text

import inngest.fast_api

from app.api.dashboard import router as dashboard_router
from app.api.dependencies import get_current_user
from app.api.tenant import get_current_tenant
from app.api.widgets import router as widgets_router
from app.api.public_widgets import router as public_widgets_router
from app.api.public_submissions import router as public_submissions_router
from app.core.database import engine
from app.core.inngest import inngest_client
from app.jobs.submission import process_submission_side_effects


app = FastAPI(
    title="FlyRank Widget Platform",
    description="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Idempotency-Key"],
)

app.include_router(widgets_router)
app.include_router(public_widgets_router)
app.include_router(public_submissions_router)
app.include_router(dashboard_router)


@app.get("/widget/v1/widget.js")
def widget_script():
    return FileResponse(
        "app/static/widget.js",
        media_type="application/javascript",
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {"database": "ok", "result": value}


@app.get("/api/v1/auth/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
    }


@app.get("/api/v1/tenant/me")
def get_my_tenant(current_tenant=Depends(get_current_tenant)):
    return {
        "id": str(current_tenant.id),
        "name": current_tenant.name,
        "supabase_user_id": current_tenant.supabase_user_id,
    }


inngest.fast_api.serve(
    app,
    inngest_client,
    [process_submission_side_effects],
)