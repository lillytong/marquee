"""Draft the pitch (Sonnet): grounded in proof-points (#2), winning examples (#1), account brief.

Anti-hallucination: the prompt forbids citing any work not in proof_points; the critique node
verifies it. If no proof-points, the model frames on affinity and sets affinity_based.
"""

from __future__ import annotations

from config import get_settings
from models.domain import OpportunityStatus
from models.state import Draft, OutreachState
from prompts.utils import render
from services import llm
from services import repositories as repo


async def draft(state: OutreachState) -> dict[str, object]:
    settings = get_settings()
    agency = await repo.get_agency()
    brand = await repo.get_brand(state.brand_id)
    contact = await repo.get_contact(state.contact_id)
    talents = {t.id: t for t in await repo.list_talents()}
    talent = talents.get(state.selected_talent_id or "")
    if agency is None or brand is None or contact is None or talent is None:
        raise ValueError("missing grounding entities for draft")

    proof_text = (
        "\n".join(f"- {p.title}: {p.relevance} [ref: {p.work_id}]" for p in state.proof_points)
        or "(none — make the case on affinity)"
    )
    experiential_text = (
        "\n\n".join(str(e["metadata"]["body"]) for e in state.experiential_examples) or "(none)"
    )
    prompt = render(
        "draft",
        brand_voice=agency.brand_voice,
        brand_name=brand.name,
        brand_industry=brand.industry,
        brand_pillars="; ".join(brand.pillars),
        contact_name=contact.name,
        contact_title=contact.title,
        account_note=state.account_note or "(none)",
        talent_name=talent.name,
        talent_category=talent.category,
        talent_angle=talent.angle,
        proof_points=proof_text,
        experiential=experiential_text,
    )
    result = await llm.structured(
        settings.model_draft,
        "You are an expert talent-agency copywriter.",
        prompt,
        Draft,
        settings.temperature_draft,
    )
    return {"draft": result, "status": OpportunityStatus.DRAFTED}
