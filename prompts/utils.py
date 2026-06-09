"""The only place prompt templates are rendered. Slots are `{name}`; other braces are left as-is."""

from __future__ import annotations

import re
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent
_SLOT = re.compile(r"\{(\w+)\}")


def render(name: str, **values: object) -> str:
    template = (PROMPTS_DIR / f"{name}.txt").read_text()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"prompt '{name}' missing slot value: {key}")
        return str(values[key])

    return _SLOT.sub(replace, template)
