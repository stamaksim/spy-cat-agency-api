"""
Application configuration.

Configuration values are loaded from environment variables (optionally from a `.env` file):
- DATABASE_URL
- THECATAPI_KEY
- BREED_CACHE_TTL_SECONDS
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file from the project root (if present).
load_dotenv()


class Settings(BaseModel):
    """Runtime settings loaded from environment variables."""

    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./sca.db"))
    thecatapi_key: str | None = Field(default=os.getenv("THECATAPI_KEY"))
    breed_cache_ttl_seconds: int = Field(
        default=int(os.getenv("BREED_CACHE_TTL_SECONDS", "3600")),
        ge=0,
        description="TTL for caching TheCatAPI breeds list (seconds).",
    )


settings = Settings()
