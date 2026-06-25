from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models import User, UserRole


def bootstrap_admin() -> None:
    if not settings.bootstrap_admin_user:
        return

    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.email == settings.first_superuser_email))
        if not admin:
            db.add(
                User(
                    email=settings.first_superuser_email,
                    hashed_password=get_password_hash(settings.first_superuser_password),
                    full_name="System Admin",
                    role=UserRole.ADMIN,
                )
            )
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    bootstrap_admin()
    yield


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.include_router(api_router)
    return application


app = create_app()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
