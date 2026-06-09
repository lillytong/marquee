"""Human approval gate — the LangGraph interrupt.

`interrupt(payload)` pauses the whole graph and surfaces `payload` to the caller (the review
surface). The run resumes via `Command(resume=decision)`; `decision` becomes interrupt()'s return.
"""

from __future__ import annotations

from langgraph.types import interrupt

from models.domain import OpportunityStatus
from models.state import OutreachState


async def approval(state: OutreachState) -> dict[str, object]:
    if state.draft is None:
        raise ValueError("no draft to approve")

    decision = interrupt(
        {
            "type": "approval_request",
            "brand_id": state.brand_id,
            "contact_id": state.contact_id,
            "selected_talent_id": state.selected_talent_id,
            "fit_score": state.fit_score,
            "affinity_based": state.draft.affinity_based,
            "subject": state.draft.subject,
            "body": state.draft.body,
        }
    )
    action = (decision or {}).get("action", "reject")

    if action == "reject":
        return {
            "approved": False,
            "status": OpportunityStatus.DROPPED,
            "drop_reason": "rejected at approval",
        }
    if action == "edit":
        edited = state.draft.model_copy(
            update={
                "subject": decision.get("subject", state.draft.subject),
                "body": decision.get("body", state.draft.body),
            }
        )
        return {"approved": True, "draft": edited, "status": OpportunityStatus.APPROVED}
    return {"approved": True, "status": OpportunityStatus.APPROVED}
