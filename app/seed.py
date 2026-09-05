from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.widget import Widget


SEED_USER_ID = "00000000-0000-0000-0000-000000000001"


def seed():
    db = SessionLocal()

    try:
        tenant = db.scalar(
            select(Tenant).where(
                Tenant.supabase_user_id == SEED_USER_ID
            )
        )

        if tenant is None:
            tenant = Tenant(
                supabase_user_id=SEED_USER_ID,
                name="FlyRank Demo Tenant",
            )

            db.add(tenant)
            db.flush()

        widget = db.scalar(
            select(Widget).where(
                Widget.tenant_id == tenant.id,
                Widget.title == "FlyRank Demo Widget",
            )
        )

        if widget is None:
            widget = Widget(
                tenant_id=tenant.id,
                type="signup",
                title="FlyRank Demo Widget",
                description="Demo widget created by the seed command.",
                fields=[
                    {
                        "name": "name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "email",
                        "type": "email",
                        "required": True,
                    },
                ],
                button_text="Submit",
                display_options={
                    "theme": "light",
                },
            )

            db.add(widget)

        db.commit()

        print("Seed completed successfully.")
        print(f"Tenant ID: {tenant.id}")

        if widget:
            print(f"Widget ID: {widget.id}")
            print(f"Public ID: {widget.public_id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()