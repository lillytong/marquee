"""Terminal: the opportunity was dropped (pre-qualify, low fit, or rejected). Reason already set."""

from __future__ import annotations

from models.domain import OpportunityStatus
from models.state import OutreachState


async def drop(state: OutreachState) -> dict[str, object]:
    return {"status": OpportunityStatus.DROPPED}
