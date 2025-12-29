"""
Cats API routes.

Provides CRUD operations for Spy Cats:
- Create a cat (breed validated via TheCatAPI)
- List cats
- Get a single cat
- Update cat salary
- Delete a cat
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.models import SpyCat
from app.db.session import get_session
from app.schemas.cats import SpyCatCreate, SpyCatRead, SpyCatSalaryUpdate
from app.services.cat_breeds import validate_breed

router = APIRouter()


@router.post(
    "",
    response_model=SpyCatRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a spy cat",
    description="Creates a new spy cat. Breed is validated using TheCatAPI.",
)
async def create_cat(payload: SpyCatCreate, session: Session = Depends(get_session)) -> SpyCat:
    """
    Create a new spy cat.

    Returns 400 if the breed is not present in TheCatAPI breeds list.
    Returns 503 if TheCatAPI is temporarily unavailable.
    """
    try:
        ok = await validate_breed(payload.breed)
    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Breed validation service unavailable (TheCatAPI).",
        ) from err

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid breed (TheCatAPI validation failed).",
        )

    cat = SpyCat(**payload.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.get(
    "",
    response_model=list[SpyCatRead],
    summary="List spy cats",
    description="Returns all spy cats ordered by id.",
)
def list_cats(session: Session = Depends(get_session)) -> list[SpyCat]:
    """List all spy cats."""
    return session.exec(select(SpyCat).order_by(SpyCat.id)).all()


@router.get(
    "/{cat_id}",
    response_model=SpyCatRead,
    summary="Get a spy cat",
    description="Returns a single spy cat by id.",
)
def get_cat(cat_id: int, session: Session = Depends(get_session)) -> SpyCat:
    """Get a spy cat by id."""
    cat = session.get(SpyCat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")
    return cat


@router.patch(
    "/{cat_id}",
    response_model=SpyCatRead,
    summary="Update spy cat salary",
    description="Updates only the salary field for a spy cat.",
)
def update_cat_salary(
    cat_id: int,
    payload: SpyCatSalaryUpdate,
    session: Session = Depends(get_session),
) -> SpyCat:
    """Update spy cat salary."""
    cat = session.get(SpyCat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")

    cat.salary = payload.salary
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.delete(
    "/{cat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a spy cat",
    description="Deletes a spy cat by id.",
)
def delete_cat(cat_id: int, session: Session = Depends(get_session)) -> None:
    """Delete a spy cat."""
    cat = session.get(SpyCat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")

    session.delete(cat)
    session.commit()
