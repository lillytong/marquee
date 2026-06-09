"""JSON extraction used by the provider-agnostic structured-output helper."""

from __future__ import annotations

from services.llm import _extract_json


def test_extract_from_code_fence() -> None:
    assert _extract_json('```json\n{"a": 1}\n```') == '{"a": 1}'


def test_extract_from_surrounding_prose() -> None:
    assert _extract_json('Here you go: {"a": 1} done').strip() == '{"a": 1}'


def test_extract_raw_json() -> None:
    assert _extract_json('{"a": 1}') == '{"a": 1}'
