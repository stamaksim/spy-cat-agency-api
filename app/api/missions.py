"""
Missions API routes.

Provides endpoints to:
- Create missions with 1..3 targets in a single request
- List missions / get a mission
- Assign a cat to a mission (one active mission per cat)
- Update mission targets: notes and completion state
- Delete missions (only if unassigned)

Business rules:
- Targets must be unique within a mission (name + country).
- Notes cannot be updated if either the target or the mission is completed.
- When all targets are completed, the mission is automatically marked as complete.
- A mission cannot be deleted after being assigned to a cat.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.models import Mission, SpyCat, Target
from app.db.session import get_session
from app.schemas.missions import MissionCreate, MissionRead, TargetUpdate

router = APIRouter()


def _load_targets(session: Session, mission_id: int) -> list[Target]:
    """Helper to load mission targets ordered by id."""
    return session.exec(
        select(Target).where(Target.mission_id == mission_id).order_by(Target.id)
    ).all()


@router.post(
    "",
    response_model=MissionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a mission",
    description="Creates a mission with 1–3 targets in a single request.",
)
def create_mission(payload: MissionCreate, session: Session = Depends(get_session)) -> Mission:
    """Create a new mission and its targets."""
    # Enforce unique targets within a mission (by name + country).
    seen: set[tuple[str, str]] = set()
    for t in payload.targets:
        key = (t.name.strip().lower(), t.country.strip().lower())
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Targets must be unique within a mission (name + country).",
            )
        seen.add(key)

    mission = Mission(cat_id=None, complete=False)
    session.add(mission)
    session.commit()
    session.refresh(mission)

    targets = [
        Target(
            mission_id=mission.id,  # type: ignore[arg-type]
            name=t.name.strip(),
            country=t.country.strip(),
            notes=t.notes,
        )
        for t in payload.targets
    ]
    session.add_all(targets)
    session.commit()

    session.refresh(mission)
    mission.targets = _load_targets(session, mission.id)  # type: ignore[arg-type]
    return mission


@router.get(
    "",
    response_model=list[MissionRead],
    summary="List missions",
    description="Returns all missions ordered by id, including their targets.",
)
def list_missions(session: Session = Depends(get_session)) -> list[Mission]:
    """List all missions (including targets)."""
    missions = session.exec(select(Mission).order_by(Mission.id)).all()
    for m in missions:
        m.targets = _load_targets(session, m.id)  # type: ignore[arg-type]
    return missions


@router.get(
    "/{mission_id}",
    response_model=MissionRead,
    summary="Get a mission",
    description="Returns a single mission by id, including its targets.",
)
def get_mission(mission_id: int, session: Session = Depends(get_session)) -> Mission:
    """Get a mission by id."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found.")
    mission.targets = _load_targets(session, mission_id)
    return mission


@router.delete(
    "/{mission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a mission",
    description="Deletes an unassigned mission. Assigned missions cannot be deleted.",
)
def delete_mission(mission_id: int, session: Session = Depends(get_session)) -> None:
    """Delete a mission if it is not assigned to a cat."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found.")
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a mission assigned to a cat.",
        )

    # If you added cascade delete to Mission.targets relationship,
    # targets will be removed automatically.
    session.delete(mission)
    session.commit()


@router.post(
    "/{mission_id}/assign/{cat_id}",
    response_model=MissionRead,
    summary="Assign a cat to a mission",
    description="Assigns a cat to a mission. A cat can have only one active mission at a time.",
)
def assign_cat(mission_id: int, cat_id: int, session: Session = Depends(get_session)) -> Mission:
    """Assign an available cat to an unassigned mission."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found.")
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Mission is already assigned."
        )

    cat = session.get(SpyCat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")

    # One active mission at a time for a cat.
    active = session.exec(
        select(Mission).where(Mission.cat_id == cat_id, Mission.complete.is_(False))
    ).first()
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This cat already has an active mission.",
        )

    mission.cat_id = cat_id
    session.add(mission)
    session.commit()
    session.refresh(mission)

    mission.targets = _load_targets(session, mission_id)
    return mission


@router.patch(
    "/{mission_id}/targets/{target_id}",
    response_model=MissionRead,
    summary="Update a mission target",
    description=(
        "Updates target notes and/or marks target as complete. "
        "Notes cannot be updated if the target or mission is completed. "
        "When all targets are completed, the mission is automatically marked as complete."
    ),
)
def update_target(
    mission_id: int,
    target_id: int,
    payload: TargetUpdate,
    session: Session = Depends(get_session),
) -> Mission:
    """Update target notes and/or completion state, enforcing business rules."""
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found.")

    target = session.get(Target, target_id)
    if not target or target.mission_id != mission_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target not found in this mission."
        )

    # Notes cannot be updated if target or mission is completed.
    if payload.notes is not None:
        if mission.complete or target.complete:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Notes are frozen for completed target/mission.",
            )
        target.notes = payload.notes

    # Completion flag update.
    if payload.complete is not None:
        if mission.complete:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Mission is already completed."
            )
        target.complete = payload.complete

    session.add(target)
    session.commit()

    # Auto-complete mission when all targets are complete.
    targets = _load_targets(session, mission_id)
    if targets and all(t.complete for t in targets):
        mission.complete = True
        session.add(mission)
        session.commit()

    session.refresh(mission)
    mission.targets = _load_targets(session, mission_id)
    return mission
