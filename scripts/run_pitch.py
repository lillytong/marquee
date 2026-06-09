"""Run one opportunity through the graph end to end (Phase 1 demo).

    uv run python scripts/run_pitch.py

Runs to the approval interrupt, prints the drafted pitch, then resumes with an 'approve' decision.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langgraph.types import Command  # noqa: E402

from agents.outreach_graph import build_graph  # noqa: E402
from models.state import OutreachState  # noqa: E402
from services import repositories as repo  # noqa: E402

BRIEF = (
    "Beauty and fragrance brands planning experiential moments around sustainability and "
    "cultural heritage this season."
)


def _get(state: Any, key: str, default: Any = None) -> Any:
    return state.get(key, default) if isinstance(state, dict) else getattr(state, key, default)


async def main() -> None:
    graph = build_graph()
    brands = {b.id: b for b in await repo.list_brands()}
    talents = {t.id: t for t in await repo.list_talents()}
    contacts = await repo.list_contacts()
    contact = next((c for c in contacts if brands[c.brand_id].name == "L'Oréal"), contacts[0])
    brand = brands[contact.brand_id]

    print(f"Campaign: {BRIEF}\n")
    print(f"Target:   {contact.name}, {contact.title} @ {brand.name} ({brand.industry})\n")

    initial = OutreachState(campaign_brief=BRIEF, brand_id=brand.id, contact_id=contact.id)
    config: Any = {"configurable": {"thread_id": f"opp-{contact.id}"}}

    result = await graph.ainvoke(initial, config)

    if "__interrupt__" not in result:
        print(
            f"Dropped before approval. status={_get(result, 'status')} "
            f"reason={_get(result, 'drop_reason')}"
        )
        return

    payload = result["__interrupt__"][0].value
    chosen = talents.get(payload["selected_talent_id"])
    print("--- pipeline reached HUMAN APPROVAL (graph paused) ---")
    print(f"fit_score:     {_get(result, 'fit_score'):.2f}  ({_get(result, 'fit_rationale')})")
    print(
        f"talent:        {chosen.name if chosen else payload['selected_talent_id']} "
        f"— {_get(result, 'selection_rationale')}"
    )
    print(
        f"proof points:  {len(_get(result, 'proof_points', []))} "
        f"(affinity_based={payload['affinity_based']})"
    )
    print(f"critique runs: {len(_get(result, 'critiques', []))}")
    print(f"\nSUBJECT: {payload['subject']}\n")
    print(payload["body"])
    print("\n--- founder approves → resuming ---\n")

    final = await graph.ainvoke(Command(resume={"action": "approve"}), config)
    print(f"status={_get(final, 'status')}  sent={_get(final, 'sent')} (Gmail dry-run)")


if __name__ == "__main__":
    asyncio.run(main())
