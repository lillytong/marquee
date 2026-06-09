"""Domain entities — also the import contract for `data/<agency>/*.json`.

These Pydantic models validate any agency's data on ingest. Persistence (SQLModel tables) and
the graph state are defined elsewhere; these are the canonical shapes everything else maps to.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class RoleType(StrEnum):
    CMO = "cmo"
    BRAND_MANAGER = "brand_manager"
    PARTNERSHIPS = "partnerships"
    COMMS_PR = "comms_pr"
    EVENTS = "events"
    OTHER = "other"


class OutcomeLabel(StrEnum):
    BOOKED = "booked"
    MEETING = "meeting"
    REPLIED = "replied"
    IGNORED = "ignored"


WINNING_OUTCOMES: frozenset[OutcomeLabel] = frozenset(
    {OutcomeLabel.BOOKED, OutcomeLabel.MEETING, OutcomeLabel.REPLIED}
)


class OpportunityStatus(StrEnum):
    SOURCED = "sourced"
    PREQUALIFIED = "prequalified"
    RESEARCHED = "researched"
    QUALIFIED = "qualified"
    DRAFTED = "drafted"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SENT = "sent"
    DROPPED = "dropped"


class AgencyProfile(BaseModel):
    id: str
    name: str
    tagline: str
    brand_voice: str = Field(description="Guidance the drafter must follow for tone/style.")


class TalentWork(BaseModel):
    """One item in a talent's archive — the unit of proof-point retrieval (#2)."""

    id: str
    title: str
    year: int
    kind: str = Field(description="e.g. live set, campaign, collab, press feature, installation")
    description: str
    tags: list[str] = Field(default_factory=list)


class Talent(BaseModel):
    id: str
    name: str
    category: str = Field(description="e.g. DJ/producer, visual artist, chef, athlete")
    bio: str
    interests: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    angle: str = Field(description="Positioning the talent is known for — drives affinity fit.")
    tags: list[str] = Field(default_factory=list)
    works: list[TalentWork] = Field(default_factory=list)


class Brand(BaseModel):
    id: str
    name: str
    industry: str
    pillars: list[str] = Field(description="Durable brand pillars — never time-sensitive events.")
    notes: str = ""


class Contact(BaseModel):
    id: str
    brand_id: str
    name: str
    title: str
    role_type: RoleType
    email: EmailStr


class PastPitch(BaseModel):
    """A previously sent pitch + its outcome — seeds experiential memory (#1)."""

    id: str
    brand_name: str
    brand_industry: str
    talent_name: str
    angle: str
    subject: str
    body: str
    outcome: OutcomeLabel

    @property
    def is_win(self) -> bool:
        return self.outcome in WINNING_OUTCOMES


class AgencyDataset(BaseModel):
    """The full validated payload for one agency — what ingestion loads from a data dir."""

    agency: AgencyProfile
    talents: list[Talent]
    brands: list[Brand]
    contacts: list[Contact]
    seed_pitches: list[PastPitch]
