"""Node logic with the LLM and repositories mocked — no network, deterministic."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

import pytest

from agents.nodes import prequalify, qualify, select
from models.domain import Brand, Contact, RoleType, Talent
from models.state import OutreachState, PrequalifyResult, QualifyResult, SelectResult

BRAND = Brand(id="b0", name="L'Oréal", industry="beauty", pillars=["sustainability"])
CONTACT = Contact(
    id="c0",
    brand_id="b0",
    name="Jun",
    title="CMO",
    role_type=RoleType.CMO,
    email="jun@example.com",
)


def _state(**kwargs: object) -> OutreachState:
    return OutreachState(campaign_brief="brief", brand_id="b0", contact_id="c0", **kwargs)


def _aret(value: Any) -> Callable[..., Coroutine[Any, Any, Any]]:
    async def _f(*_args: Any, **_kwargs: Any) -> Any:
        return value

    return _f


async def test_prequalify_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.repositories.get_brand", _aret(BRAND))
    monkeypatch.setattr("services.repositories.get_contact", _aret(CONTACT))
    monkeypatch.setattr(
        "services.llm.structured", _aret(PrequalifyResult(worth_pursuing=True, reason="ok"))
    )
    out = await prequalify.prequalify(_state())
    assert out["prequalified"] is True


async def test_prequalify_drop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.repositories.get_brand", _aret(BRAND))
    monkeypatch.setattr("services.repositories.get_contact", _aret(CONTACT))
    monkeypatch.setattr(
        "services.llm.structured",
        _aret(PrequalifyResult(worth_pursuing=False, reason="wrong industry")),
    )
    out = await prequalify.prequalify(_state())
    assert out["prequalified"] is False
    assert str(out["status"]) == "dropped"


async def test_qualify_sets_score(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.repositories.get_brand", _aret(BRAND))
    monkeypatch.setattr(
        "services.llm.structured", _aret(QualifyResult(fit_score=0.82, rationale="r"))
    )
    out = await qualify.qualify(_state())
    assert out["fit_score"] == 0.82


async def test_select_falls_back_on_invalid_id(monkeypatch: pytest.MonkeyPatch) -> None:
    talents = [Talent(id="t0", name="Léa", category="perfumer", bio="b", angle="eco")]
    monkeypatch.setattr("services.repositories.get_brand", _aret(BRAND))
    monkeypatch.setattr("services.repositories.list_talents", _aret(talents))
    monkeypatch.setattr(
        "services.llm.structured", _aret(SelectResult(talent_id="nope", rationale="r"))
    )
    out = await select.select(_state())
    assert out["selected_talent_id"] == "t0"
