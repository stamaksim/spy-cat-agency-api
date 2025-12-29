"""
Pydantic schemas for Spy Cats.

These models define request/response payloads for the Cats API.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SpyCatCreate(BaseModel):
    """Payload used to create a new spy cat."""

    name: str = Field(..., min_length=1, description="Cat name.")
    years_of_experience: int = Field(
        ...,
        ge=0,
        description="Years of spying experience (non-negative integer).",
    )
    breed: str = Field(..., min_length=1, description="Cat breed (validated via TheCatAPI).")
    salary: int = Field(..., ge=0, description="Monthly salary in USD (non-negative integer).")


class SpyCatRead(BaseModel):
    """Spy cat representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    years_of_experience: int
    breed: str
    salary: int


class SpyCatSalaryUpdate(BaseModel):
    """Payload used to update a spy cat salary."""

    salary: int = Field(..., ge=0, description="New monthly salary in USD (non-negative integer).")
