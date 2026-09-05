from fastapi import Depends, FastAPI
from sqlalchemy import text

from app.api.dependencies import get_current_user
from app.api.tenant import get_current_tenant
from app.core.database import engine
from app.api.widgets import router as widgets_router

app = FastAPI(
    title="FlyRank Widget Platform",
    description="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0",
)

app.include_router(widgets_router)

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