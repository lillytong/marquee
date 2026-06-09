"""Research (MOCKED in Phase 1, no LLM): synthesizes signals from durable brand data.

Production does live, just-in-time web research behind a services/ interface — never cached.
"""

from __future__ import annotations

from models.domain import OpportunityStatus
from models.state import OutreachState, ResearchSummary
from services import repositories as repo


async def research(state: OutreachState) -> dict[str, object]:
    brand = await repo.get_brand(state.brand_id)
    if brand is None:
        raise ValueError("brand not found in store")

    summary = (
        f"{brand.name} is a {brand.industry} brand. Durable pillars: {', '.join(brand.pillars)}."
    )
    return {
        "research": ResearchSummary(summary=summary, signals=list(brand.pillars)),
        "status": OpportunityStatus.RESEARCHED,
    }
