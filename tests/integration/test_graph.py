"""Full graph wiring with everything mocked — proves routing, the interrupt, and resume.

Deterministic and offline (no LLM, no stores), so it is safe to run in CI.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from langgraph.types import Command

from agents.outreach_graph import build_graph
from models.domain import AgencyProfile, Brand, Contact, RoleType, Talent
from models.state import (
    Critique,
    Draft,
    OutreachState,
    PrequalifyResult,
    QualifyResult,
    SelectResult,
)

AGENCY = AgencyProfile(id="agency", name="Atelier", tagline="t", brand_voice="warm")
BRAND = Brand(id="b0", name="L'Oréal", industry="beauty", pillars=["sustainability"])
CONTACT = Contact(
    id="c0",
    brand_id="b0",
    name="Jun",
    title="CMO",
    role_type=RoleType.CMO,
    email="jun@example.com",
)
TALENTS = [Talent(id="t0", name="Léa", category="perfumer", bio="b", angle="eco")]

_CANNED: dict[type, Any] = {
    PrequalifyResult: PrequalifyResult(worth_pursuing=True, reason="ok"),
    QualifyResult: QualifyResult(fit_score=0.9, rationale="great"),
    SelectResult: SelectResult(talent_id="t0", rationale="fit"),
    Draft: Draft(subject="S", body="B", used_proof_point_ids=[], affinity_based=True),
    Critique: Critique(passed=True, score=0.9, issues=[]),
}


async def _fake_structured(
    model: str, system: str, user: str, schema: type, temperature: float = 0.0
) -> Any:
    return _CANNED[schema]


def _aret(value: Any) -> Callable[..., Coroutine[Any, Any, Any]]:
    async def _f(*_args: Any, **_kwargs: Any) -> Any:
        return value

    return _f


@pytest.fixture
def _mock_world(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.llm.structured", _fake_structured)
    monkeypatch.setattr("services.repositories.get_agency", _aret(AGENCY))
    monkeypatch.setattr("services.repositories.get_brand", _aret(BRAND))
    monkeypatch.setattr("services.repositories.get_contact", _aret(CONTACT))
    monkeypatch.setattr("services.repositories.list_talents", _aret(TALENTS))
    monkeypatch.setattr("memory.experiential.ExperientialMemory.retrieve_similar_wins", _aret([]))
    monkeypatch.setattr("memory.talent_archive.TalentArchive.retrieve_proof_points", _aret([]))


def _initial() -> OutreachState:
    return OutreachState(campaign_brief="b", brand_id="b0", contact_id="c0")


async def test_runs_to_interrupt_then_sends_on_approve(_mock_world: None) -> None:
    graph = build_graph()
    config: Any = {"configurable": {"thread_id": "t-approve"}}

    result = await graph.ainvoke(_initial(), config)
    assert "__interrupt__" in result  # paused at the human approval gate

    final = await graph.ainvoke(Command(resume={"action": "approve"}), config)
    assert final["sent"] is True
    assert str(final["status"]) == "sent"


async def test_drops_on_reject(_mock_world: None) -> None:
    graph = build_graph()
    config: Any = {"configurable": {"thread_id": "t-reject"}}

    await graph.ainvoke(_initial(), config)
    final = await graph.ainvoke(Command(resume={"action": "reject"}), config)
    assert final["sent"] is False
    assert str(final["status"]) == "dropped"
