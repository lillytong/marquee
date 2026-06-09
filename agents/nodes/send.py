"""Send (DRY-RUN in Phase 1): would create a Gmail draft; never auto-sends. Records the outcome."""

from __future__ import annotations

from models.domain import OpportunityStatus
from models.state import OutreachState


async def send(state: OutreachState) -> dict[str, object]:
    # Dry-run: production creates a Gmail draft via services/gmail (gated by MARQUEE_GMAIL_DRY_RUN).
    return {"sent": True, "status": OpportunityStatus.SENT}
