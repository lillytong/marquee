"""Cheap pre-filter (Haiku): drop obvious mismatches before expensive research."""

from __future__ import annotations

from config import get_settings
from models.domain import OpportunityStatus
from models.state import OutreachState, PrequalifyResult
from prompts.utils import render
from services import llm
from services import repositories as repo


async def prequalify(state: OutreachState) -> dict[str, object]:
    settings = get_settings()
    brand = await repo.get_brand(state.brand_id)
    contact = await repo.get_contact(state.contact_id)
    if brand is None or contact is None:
        raise ValueError("brand or contact not found in store")

    prompt = render(
        "prequalify",
        brief=state.campaign_brief,
        brand_name=brand.name,
        brand_industry=brand.industry,
        brand_pillars="; ".join(brand.pillars),
        contact_title=contact.title,
        contact_role=contact.role_type.value,
    )
    result = await llm.structured(
        settings.model_triage,
        "You triage B2B outreach targets for a talent agency.",
        prompt,
        PrequalifyResult,
        settings.temperature_deterministic,
    )
    if not result.worth_pursuing:
        return {
            "prequalified": False,
            "status": OpportunityStatus.DROPPED,
            "drop_reason": result.reason,
        }
    return {"prequalified": True, "status": OpportunityStatus.PREQUALIFIED}
