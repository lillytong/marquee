"""Evaluators. The pitch-quality judge deliberately uses a DIFFERENT model from the task models
(config.judge_model) to avoid self-preference bias, and is calibrated against human labels."""

from __future__ import annotations

from pydantic import BaseModel

from config import get_settings
from prompts.utils import render
from services import llm


class JudgeVerdict(BaseModel):
    follows_brand_voice: float
    specificity: float
    leads_with_brand: bool
    fabricated_proof: bool
    overall_score: float
    passed: bool
    notes: str = ""


async def judge_pitch(
    *, subject: str, body: str, brand_voice: str, allowed_proof_points: str
) -> JudgeVerdict:
    settings = get_settings()
    prompt = render(
        "judge_pitch",
        brand_voice=brand_voice,
        allowed_proof_points=allowed_proof_points or "(none)",
        subject=subject,
        body=body,
    )
    return await llm.structured(
        settings.judge_model,
        "You are an impartial reviewer scoring outreach pitches.",
        prompt,
        JudgeVerdict,
        settings.temperature_deterministic,
    )
