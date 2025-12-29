"""
API router registry.

All application routers are included here to keep `app/main.py` minimal.
"""

from fastapi import APIRouter

from app.api.cats import router as cats_router
from app.api.missions import router as missions_router

api_router = APIRouter()

api_router.include_router(cats_router, prefix="/cats", tags=["cats"])
api_router.include_router(missions_router, prefix="/missions", tags=["missions"])
