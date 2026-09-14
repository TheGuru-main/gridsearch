"""
SQLAlchemy engine + session for Neon Postgres.
Reads DATABASE_URL from env. Handles the postgresql:// → psycopg:// rewrite
so the same connection string works locally and on Render.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


def _normalize_url(url: str) -> str:
    """Neon gives postgresql://... — SQLAlchemy wants a driver prefix."""
    if not url:
        return url
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _normalize_url(os.environ.get("DATABASE_URL", ""))

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add your Neon connection string "
        "to the environment (e.g. postgresql://user:pass@host/db?sslmode=require)."
    )


# Neon serverless: use small pool, recycle aggressively, pre-ping to survive cold starts.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # reconnect if Neon has hibernated
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,        # 30 min — Neon closes idle connections
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db():
    """FastAPI dependency: yields a session, closes when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call multiple times."""
    import models  # noqa: F401 — ensures models are registered on Base
    Base.metadata.create_all(bind=engine)