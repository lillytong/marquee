"""LangGraph execution state (Plane 1). Small working set; references stores by id."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from models.domain import OpportunityStatus


class ResearchSummary(BaseModel):
    summary: str
    signals: list[str] = Field(default_factory=list)


class Critique(BaseModel):
    passed: bool
    score: float
    issues: list[str] = Field(default_factory=list)


class ProofPoint(BaseModel):
    work_id: str
    title: str
    relevance: str


class Draft(BaseModel):
    subject: str
    body: str
    used_proof_point_ids: list[str] = Field(default_factory=list)
    affinity_based: bool = Field(
        default=False, description="True when no proof-points retrieved → framed on affinity."
    )


# --- Node structured-output schemas (what each LLM node is forced to return) ---


class PrequalifyResult(BaseModel):
    worth_pursuing: bool
    reason: str


class QualifyResult(BaseModel):
    fit_score: float
    rationale: str


class SelectResult(BaseModel):
    talent_id: str
    rationale: str


class OutreachState(BaseModel):
    """State for one opportunity (one pitch). One graph thread per opportunity."""

    campaign_brief: str
    brand_id: str
    contact_id: str

    status: OpportunityStatus = OpportunityStatus.SOURCED
    prequalified: bool | None = None
    research: ResearchSummary | None = None
    fit_score: float | None = None
    fit_rationale: str | None = None

    selected_talent_id: str | None = None
    selection_rationale: str | None = None
    proof_points: list[ProofPoint] = Field(default_factory=list)
    experiential_examples: list[dict[str, Any]] = Field(default_factory=list)
    account_note: str | None = None

    draft: Draft | None = None
    critiques: list[Critique] = Field(default_factory=list)
    revision_count: int = 0

    approved: bool | None = None
    sent: bool = False
    drop_reason: str | None = None
