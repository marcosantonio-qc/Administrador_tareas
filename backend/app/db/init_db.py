from __future__ import annotations
import time
from sqlalchemy import text, create_engine
from sqlalchemy.engine import make_url
from app.core.config import get_settings
from app.db.base import Base


def ensure_database_and_tables():
    settings = get_settings()
    url = make_url(settings.database_url)
    # Ensure database exists by connecting to master first
    master_url = url.set(database="master")

    # Wait for server to be available
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        try:
            with create_engine(master_url, pool_pre_ping=True).connect() as conn:
                conn.execute(text("IF DB_ID(:dbname) IS NULL BEGIN EXEC('CREATE DATABASE ' + QUOTENAME(:dbname)); END"), {"dbname": url.database})
                break
        except Exception as exc:
            if attempt == max_attempts:
                raise
            time.sleep(2)

    # Now create tables in target DB
    engine = create_engine(url, pool_pre_ping=True)
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
