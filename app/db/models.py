"""
SQLModel database models for the Spy Cat Agency API.

Entities:
- SpyCat: a cat hired by the agency.
- Mission: a mission that may be assigned to a cat and contains 1..3 targets.
- Target: a single target within a mission, with notes and completion status.

Notes:
- Targets exist only inside a mission (no standalone targets endpoints).
- Deleting a mission should also delete its targets (cascade delete is enabled).
- Business rules such as "one active mission per cat" or "freeze notes after completion"
  are enforced at the API/service layer, not at the database schema level.
"""

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class SpyCat(SQLModel, table=True):
    """Represents a spy cat hired by the agency."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    years_of_experience: int = Field(ge=0)
    breed: str
    salary: int = Field(ge=0)

    # A cat may have multiple missions historically,
    # but API enforces only one active (not completed) mission at a time.
    missions: List["Mission"] = Relationship(back_populates="cat")


class Mission(SQLModel, table=True):
    """A mission that can be assigned to a cat and contains 1..3 targets."""

    id: int | None = Field(default=None, primary_key=True)
    cat_id: int | None = Field(default=None, foreign_key="spycat.id", index=True)
    complete: bool = Field(default=False)

    # Relationship to the assigned cat (nullable until assigned).
    cat: Optional["SpyCat"] = Relationship(back_populates="missions")

    # Targets belong to a mission and should be deleted together with the mission.
    targets: List["Target"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Target(SQLModel, table=True):
    """A target within a mission."""

    id: int | None = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="mission.id", index=True)

    name: str
    country: str
    notes: str = Field(default="")
    complete: bool = Field(default=False)

    # Back-reference to the mission this target belongs to.
    mission: Optional["Mission"] = Relationship(back_populates="targets")
