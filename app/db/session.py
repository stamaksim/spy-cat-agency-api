"""
Database session and engine configuration.

- Creates SQLAlchemy/SQLModel engine using DATABASE_URL from settings.
- Initializes schema (create_all) on application startup.
- Provides a FastAPI dependency for DB sessions.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# SQLite requires this flag for multi-threaded usage (e.g. FastAPI + TestClient).
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
)


def init_db() -> None:
    """Create database tables if they do not exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session.

    Usage:
        def endpoint(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
