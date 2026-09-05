from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.tenant import Tenant


def get_current_tenant(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    user_id = str(current_user.id)

    tenant = db.scalar(
        select(Tenant).where(
            Tenant.supabase_user_id == user_id
        )
    )

    if tenant is None:
        tenant = Tenant(
            supabase_user_id=user_id,
            name=current_user.email or "Customer",
        )

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    return tenant