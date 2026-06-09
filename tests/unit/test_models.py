"""Domain model logic — the winners-only definition used by experiential retrieval."""

from __future__ import annotations

from models.domain import OutcomeLabel, PastPitch


def _pitch(outcome: OutcomeLabel) -> PastPitch:
    return PastPitch(
        id="x",
        brand_name="b",
        brand_industry="i",
        talent_name="t",
        angle="a",
        subject="s",
        body="body",
        outcome=outcome,
    )


def test_is_win() -> None:
    assert _pitch(OutcomeLabel.BOOKED).is_win
    assert _pitch(OutcomeLabel.MEETING).is_win
    assert _pitch(OutcomeLabel.REPLIED).is_win
    assert not _pitch(OutcomeLabel.IGNORED).is_win
