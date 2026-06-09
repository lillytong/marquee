"""Full fit-score (Haiku): how well this brand fits the campaign brief."""

from __future__ import annotations

from config import get_settings
from models.domain import OpportunityStatus
from models.state import OutreachState, QualifyResult
from prompts.utils import render
from services import llm
from services import repositories as repo


async def qualify(state: OutreachState) -> dict[str, object]:
    settings = get_settings()
    brand = await repo.get_brand(state.brand_id)
    if brand is None:
        raise ValueError("brand not found in store")

    signals = "; ".join(state.research.signals) if state.research else ""
    prompt = render(
        "qualify",
        brief=state.campaign_brief,
        brand_name=brand.name,
        brand_industry=brand.industry,
        brand_pillars="; ".join(brand.pillars),
        research_signals=signals,
    )
    result = await llm.structured(
        settings.model_qualify,
        "You score brand fit for talent-agency outreach.",
        prompt,
        QualifyResult,
        settings.temperature_deterministic,
    )
    return {
        "fit_score": result.fit_score,
        "fit_rationale": result.rationale,
        "status": OpportunityStatus.QUALIFIED,
    }
