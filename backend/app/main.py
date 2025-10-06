from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models import models  # noqa: F401
from app.routers import events, rooms, auth, users
from app.middleware.rate_limit import RateLimitMiddleware
from app.db.init_db import ensure_database_and_tables

app = FastAPI(title="Club Events Calendar")
app.add_middleware(RateLimitMiddleware, max_requests=300, window_seconds=60)


@app.on_event("startup")
def on_startup():
    # Ensure database exists and create tables
    ensure_database_and_tables()
    # create seed admin if none exists
    from app.core.security import hash_password
    from app.models.models import User, RoleEnum
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(email="admin@example.com", full_name="Admin", password_hash=hash_password("Admin123!"), role=RoleEnum.admin)
            db.add(admin)
            db.commit()
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(events.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
