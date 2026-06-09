"""Critique (Sonnet): score the draft and enforce the anti-hallucination guardrail.

Returns a Critique appended to state. The router (in the graph file) decides loop-back vs. proceed.
"""

from __future__ import annotations

from config import get_settings
from models.state import Critique, OutreachState
from prompts.utils import render
from services import llm
from services import repositories as repo


async def critique(state: OutreachState) -> dict[str, object]:
    settings = get_settings()
    agency = await repo.get_agency()
    if agency is None or state.draft is None:
        raise ValueError("missing agency or draft for critique")

    allowed = "\n".join(f"- {p.title}: {p.relevance}" for p in state.proof_points) or "(none)"
    prompt = render(
        "critique",
        brand_voice=agency.brand_voice,
        allowed_proof_points=allowed,
        subject=state.draft.subject,
        body=state.draft.body,
    )
    result = await llm.structured(
        settings.model_critique,
        "You are a strict editor protecting a brand relationship.",
        prompt,
        Critique,
        settings.temperature_deterministic,
    )
    revised = [*state.critiques, result]
    return {"critiques": revised, "revision_count": len(revised)}
