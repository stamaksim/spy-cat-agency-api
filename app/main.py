"""
Application entrypoint for the Spy Cat Agency API.

- Initializes the database on startup.
- Registers API routers.
- Provides a basic healthcheck endpoint.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Runs on startup/shutdown. We create DB schema on startup to keep local setup
    simple for the test assignment.
    """
    init_db()
    yield


app = FastAPI(
    title="Spy Cat Agency API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get(
    "/health",
    tags=["default"],
    summary="Health check",
    description="Simple endpoint used to verify that the service is running.",
)
def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
