"""
Pydantic schemas for Missions and Targets.

These models define the request/response payloads for the Missions API.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TargetCreate(BaseModel):
    """Payload used when creating a target as part of a mission."""

    name: str = Field(..., min_length=1, description="Target name (unique within a mission).")
    country: str = Field(..., min_length=1, description="Target country.")
    notes: str = Field("", description="Initial notes for the target.")


class TargetRead(BaseModel):
    """Target representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str
    notes: str
    complete: bool


class TargetUpdate(BaseModel):
    """
    Payload for updating a target.

    - `notes` can be updated while both the target and mission are not completed.
    - `complete` marks the target as completed.
    """

    notes: str | None = Field(None, description="Updated notes for the target.")
    complete: bool | None = Field(None, description="Mark target as completed.")


class MissionCreate(BaseModel):
    """Payload used when creating a mission with its targets."""

    targets: list[TargetCreate] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Targets for the mission (min 1, max 3).",
    )


class MissionRead(BaseModel):
    """Mission representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cat_id: int | None = Field(None, description="Assigned cat id (null if unassigned).")
    complete: bool
    targets: list[TargetRead]
