"""Prompt rendering — slot substitution and the missing-slot guard."""

from __future__ import annotations

import pytest

from prompts.utils import render


def test_render_substitutes_all_slots() -> None:
    out = render(
        "qualify",
        brief="my brief",
        brand_name="L'Oréal",
        brand_industry="beauty",
        brand_pillars="sustainability",
        research_signals="signal",
    )
    assert "my brief" in out
    assert "{brief}" not in out
    assert "{brand_pillars}" not in out


def test_render_missing_slot_raises() -> None:
    with pytest.raises(KeyError):
        render("qualify", brief="only one provided")
