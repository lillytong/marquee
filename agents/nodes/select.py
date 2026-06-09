"""Talent selection (Haiku): pick the single best-fit talent, in-context over the whole roster.

No RAG here — 50 compact bios fit in context. Weighs demonstrated AND affinity fit.
"""

from __future__ import annotations

from config import get_settings
from models.state import OutreachState, SelectResult
from prompts.utils import render
from services import llm
from services import repositories as repo


async def select(state: OutreachState) -> dict[str, object]:
    settings = get_settings()
    brand = await repo.get_brand(state.brand_id)
    talents = await repo.list_talents()
    if brand is None or not talents:
        raise ValueError("brand or roster missing")

    roster = "\n".join(
        f"{t.id} | {t.name} | {t.category} | {t.angle} | {', '.join(t.tags)}" for t in talents
    )
    prompt = render(
        "select_talent",
        brief=state.campaign_brief,
        brand_name=brand.name,
        brand_industry=brand.industry,
        brand_pillars="; ".join(brand.pillars),
        roster=roster,
    )
    result = await llm.structured(
        settings.model_select,
        "You match agency talent to brand opportunities.",
        prompt,
        SelectResult,
        settings.temperature_deterministic,
    )
    valid_ids = {t.id for t in talents}
    talent_id = result.talent_id if result.talent_id in valid_ids else talents[0].id
    return {"selected_talent_id": talent_id, "selection_rationale": result.rationale}
