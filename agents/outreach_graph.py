"""Graph assembly — the ONLY place StateGraph/add_node/add_edge/compile live.

Routers below are orchestration (they decide what runs next from state); per the architecture
rules they belong here, not in the node files.
"""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.nodes import (
    approval,
    critique,
    draft,
    drop,
    grounding,
    prequalify,
    qualify,
    research,
    select,
    send,
)
from config import get_settings
from models.state import OutreachState


def _route_prequalify(state: OutreachState) -> str:
    return "research" if state.prequalified else "drop"


def _route_qualify(state: OutreachState) -> str:
    threshold = get_settings().fit_threshold
    return "select" if (state.fit_score or 0.0) >= threshold else "drop"


def _route_critique(state: OutreachState) -> str:
    """Loop back to draft while the critique fails and we have revisions left; else proceed."""
    last = state.critiques[-1]
    if last.passed:
        return "approval"
    if len(state.critiques) > get_settings().max_revisions:
        return "approval"  # give up revising; let the human decide
    return "draft"


def _route_approval(state: OutreachState) -> str:
    return "send" if state.approved else "drop"


def build_graph() -> CompiledStateGraph[Any, Any, Any, Any]:
    g: StateGraph[Any, Any, Any, Any] = StateGraph(OutreachState)

    g.add_node("prequalify", prequalify.prequalify)
    g.add_node("research", research.research)
    g.add_node("qualify", qualify.qualify)
    g.add_node("select", select.select)
    g.add_node("grounding", grounding.grounding)
    g.add_node("draft", draft.draft)
    g.add_node("critique", critique.critique)
    g.add_node("approval", approval.approval)
    g.add_node("send", send.send)
    g.add_node("drop", drop.drop)

    g.add_edge(START, "prequalify")
    g.add_conditional_edges(
        "prequalify", _route_prequalify, {"research": "research", "drop": "drop"}
    )
    g.add_edge("research", "qualify")
    g.add_conditional_edges("qualify", _route_qualify, {"select": "select", "drop": "drop"})
    g.add_edge("select", "grounding")
    g.add_edge("grounding", "draft")
    g.add_edge("draft", "critique")
    g.add_conditional_edges("critique", _route_critique, {"draft": "draft", "approval": "approval"})
    g.add_conditional_edges("approval", _route_approval, {"send": "send", "drop": "drop"})
    g.add_edge("send", END)
    g.add_edge("drop", END)

    # In-memory checkpointer for Phase 1; the durable SQLite saver swaps in for the Phase 2 cadence.
    return g.compile(checkpointer=MemorySaver())
