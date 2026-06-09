"""Conditional-edge routers — pure functions, the orchestration logic of the graph."""

from __future__ import annotations

from agents.outreach_graph import (
    _route_approval,
    _route_critique,
    _route_prequalify,
    _route_qualify,
)
from models.state import Critique, OutreachState


def _state(**kwargs: object) -> OutreachState:
    return OutreachState(campaign_brief="b", brand_id="b0", contact_id="c0", **kwargs)


def test_prequalify_drop_vs_research() -> None:
    assert _route_prequalify(_state(prequalified=False)) == "drop"
    assert _route_prequalify(_state(prequalified=True)) == "research"


def test_qualify_threshold() -> None:
    assert _route_qualify(_state(fit_score=0.9)) == "select"
    assert _route_qualify(_state(fit_score=0.1)) == "drop"


def test_critique_passes_to_approval() -> None:
    state = _state(critiques=[Critique(passed=True, score=0.9)])
    assert _route_critique(state) == "approval"


def test_critique_fail_loops_back_to_draft() -> None:
    state = _state(critiques=[Critique(passed=False, score=0.2)])
    assert _route_critique(state) == "draft"


def test_critique_gives_up_after_max_revisions() -> None:
    # default max_revisions = 2, so a 3rd failed critique stops the loop
    fails = [Critique(passed=False, score=0.2) for _ in range(3)]
    assert _route_critique(_state(critiques=fails)) == "approval"


def test_approval_routes() -> None:
    assert _route_approval(_state(approved=True)) == "send"
    assert _route_approval(_state(approved=False)) == "drop"
