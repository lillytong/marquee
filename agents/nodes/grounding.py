"""Gather grounding (no LLM): the two memories + account brief, feeding the drafter.

- #1 experiential: similar WINNING past pitches (semantic, winners-only).
- #2 proof-points: the CHOSEN talent's relevant works (semantic, scoped to talent_id). May be empty.
- account brief: prior interactions with this brand (Phase 1: none for fresh contacts).
"""

from __future__ import annotations

from memory.experiential import ExperientialMemory
from memory.talent_archive import TalentArchive
from models.state import OutreachState, ProofPoint
from services import repositories as repo


async def grounding(state: OutreachState) -> dict[str, object]:
    brand = await repo.get_brand(state.brand_id)
    if brand is None or state.selected_talent_id is None:
        raise ValueError("brand missing or no talent selected")

    angle = brand.pillars[0] if brand.pillars else state.campaign_brief
    query = f"{state.campaign_brief}. {'; '.join(brand.pillars)}"

    experiential = await ExperientialMemory().retrieve_similar_wins(
        industry=brand.industry, angle=angle, k=3
    )
    proof_raw = await TalentArchive().retrieve_proof_points(
        talent_id=state.selected_talent_id, query_text=query, k=3
    )
    proof_points = [
        ProofPoint(
            work_id=p["id"],
            title=str(p["metadata"]["title"]),
            relevance=str(p["document"])[:200],
        )
        for p in proof_raw
    ]
    return {
        "experiential_examples": experiential,
        "proof_points": proof_points,
        "account_note": "No prior interactions on record.",
    }
