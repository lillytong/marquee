"""Provider-agnostic LLM layer (LiteLLM-backed via ChatLiteLLM).

Models are chosen by config per task — never hardcoded in nodes. Structured output is done by
instructing JSON and validating into a Pydantic model, so it works across providers (no reliance
on a single vendor's tool-calling dialect).
"""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from pydantic import BaseModel

from config import get_settings

get_settings().apply_provider_env()


def _chat(model: str, temperature: float | None) -> ChatLiteLLM:
    if temperature is None:
        return ChatLiteLLM(model=model)
    return ChatLiteLLM(model=model, temperature=temperature)


async def complete(model: str, system: str, user: str, temperature: float = 0.0) -> str:
    messages = [SystemMessage(content=system), HumanMessage(content=user)]
    try:
        resp = await _chat(model, temperature).ainvoke(messages)
    except Exception as exc:  # noqa: BLE001 — some models (e.g. Opus 4.8) reject `temperature`
        if "temperature" not in str(exc).lower():
            raise
        resp = await _chat(model, None).ainvoke(messages)
    return resp.content if isinstance(resp.content, str) else str(resp.content)


def _extract_json(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    braces = re.search(r"\{.*\}", text, re.DOTALL)
    return braces.group(0) if braces else text


async def structured[T: BaseModel](
    model: str, system: str, user: str, schema: type[T], temperature: float = 0.0
) -> T:
    """Call the model and validate its output into `schema`. Retries once on parse failure."""
    instruction = (
        "\n\nReturn ONLY a JSON object (no prose, no markdown) conforming to this JSON schema:\n"
        + json.dumps(schema.model_json_schema())
    )
    full_system = system + instruction
    last_error: Exception | None = None
    for _ in range(2):
        raw = await complete(model, full_system, user, temperature)
        try:
            return schema.model_validate_json(_extract_json(raw))
        except Exception as exc:  # noqa: BLE001 — validation/JSON errors trigger a retry
            last_error = exc
            user = f"{user}\n\nYour previous reply did not parse ({exc}). Return valid JSON only."
    raise ValueError(f"structured() failed after retries: {last_error}")
