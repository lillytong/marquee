"""Run the Marquee eval suite and print a scorecard. Real LLM calls — NOT part of CI.

    uv run python scripts/seed.py --from data/mock     # retrieval evals need seeded stores
    uv run python evals/run_evals.py

Measures quality, not correctness (that is what tests/ are for). If LANGSMITH_TRACING=true, every
call here is traced to LangSmith for inspection.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import get_settings  # noqa: E402
from evals.datasets import (  # noqa: E402
    AGENCY_VOICE,
    CALIBRATION_CASES,
    PITCH_CASES,
    QUALIFICATION_CASES,
    PitchCase,
    QualificationCase,
)
from evals.evaluators import judge_pitch  # noqa: E402
from memory.experiential import ExperientialMemory  # noqa: E402
from memory.talent_archive import TalentArchive  # noqa: E402
from models.state import Draft, QualifyResult  # noqa: E402
from prompts.utils import render  # noqa: E402
from services import llm  # noqa: E402
from services import repositories as repo  # noqa: E402

PROOF_THEMES = {"sustainability", "eco", "zero-waste"}


async def _qualify_predicts_fit(case: QualificationCase) -> bool:
    settings = get_settings()
    prompt = render(
        "qualify",
        brief=case.brief,
        brand_name=case.brand_name,
        brand_industry=case.brand_industry,
        brand_pillars="; ".join(case.brand_pillars),
        research_signals="; ".join(case.brand_pillars),
    )
    result = await llm.structured(
        settings.model_qualify,
        "You score brand fit for talent-agency outreach.",
        prompt,
        QualifyResult,
        settings.temperature_deterministic,
    )
    return result.fit_score >= settings.fit_threshold


async def _generate_draft(case: PitchCase) -> Draft:
    settings = get_settings()
    proof_text = (
        "\n".join(f"- {p.title}: {p.relevance} [ref: {p.work_id}]" for p in case.proof_points)
        or "(none — make the case on affinity)"
    )
    prompt = render(
        "draft",
        brand_voice=AGENCY_VOICE,
        brand_name=case.brand_name,
        brand_industry=case.brand_industry,
        brand_pillars="; ".join(case.brand_pillars),
        contact_name=case.contact_name,
        contact_title=case.contact_title,
        account_note="(none)",
        talent_name=case.talent_name,
        talent_category=case.talent_category,
        talent_angle=case.talent_angle,
        proof_points=proof_text,
        experiential="\n\n".join(case.experiential) or "(none)",
    )
    return await llm.structured(
        settings.model_draft,
        "You are an expert talent-agency copywriter.",
        prompt,
        Draft,
        settings.temperature_draft,
    )


async def eval_qualification() -> tuple[float, list[str]]:
    rows: list[str] = []
    correct = 0
    for case in QUALIFICATION_CASES:
        predicted = await _qualify_predicts_fit(case)
        ok = predicted == case.expected_fit
        correct += ok
        rows.append(
            f"    {case.id} {case.brand_name:<10} pred={'fit ' if predicted else 'nofit'} "
            f"exp={'fit ' if case.expected_fit else 'nofit'}  {'ok' if ok else 'MISS'}"
        )
    return correct / len(QUALIFICATION_CASES), rows


async def eval_retrieval() -> list[str]:
    rows: list[str] = []
    exp = await ExperientialMemory().retrieve_similar_wins(
        industry="beauty", angle="sustainability", k=5
    )
    if not exp:
        return ["    (stores empty — run `python scripts/seed.py --from data/mock` first)"]
    winners = sum(1 for r in exp if r["metadata"]["is_win"]) / len(exp)
    rows.append(f"    experiential winners-only precision: {winners:.2f} (target 1.00)")

    talents = await repo.list_talents()
    themed = next((t for t in talents if "sustainability" in t.tags), talents[0])
    proof = await TalentArchive().retrieve_proof_points(
        talent_id=themed.id, query_text="sustainability zero-waste eco", k=5
    )
    if proof:
        scoped = sum(1 for r in proof if r["metadata"]["talent_id"] == themed.id) / len(proof)
        relevant = sum(
            1 for r in proof if PROOF_THEMES & set(str(r["metadata"]["tags"]).split(", "))
        ) / len(proof)
        rows.append(f"    proof-point talent-scoping precision: {scoped:.2f} (target 1.00)")
        rows.append(f"    proof-point theme relevance@5:        {relevant:.2f}")
    return rows


async def eval_pitches() -> list[str]:
    rows: list[str] = []
    citation_ok = 0
    affinity_ok = 0
    quality_pass = 0
    for case in PITCH_CASES:
        draft = await _generate_draft(case)
        allowed = {p.work_id for p in case.proof_points}
        cited = set(draft.used_proof_point_ids)
        integrity = cited <= allowed
        citation_ok += integrity
        if not case.proof_points:
            affinity_ok += draft.affinity_based and not cited
        allowed_text = (
            "\n".join(f"- {p.title}: {p.relevance}" for p in case.proof_points) or "(none)"
        )
        verdict = await judge_pitch(
            subject=draft.subject,
            body=draft.body,
            brand_voice=AGENCY_VOICE,
            allowed_proof_points=allowed_text,
        )
        quality_pass += verdict.passed
        rows.append(
            f"    {case.id:<16} cite_ok={integrity!s:<5} judge_pass={verdict.passed!s:<5} "
            f"score={verdict.overall_score:.2f} voice={verdict.follows_brand_voice:.2f}"
        )
    n = len(PITCH_CASES)
    rows.append(f"    -> citation integrity: {citation_ok}/{n}  judge-pass: {quality_pass}/{n}")
    rows.append(f"    -> affinity-path correctness (p3): {'ok' if affinity_ok else 'MISS'}")
    return rows


async def eval_judge_calibration() -> tuple[float, list[str]]:
    rows: list[str] = []
    agree = 0
    for case in CALIBRATION_CASES:
        allowed_text = (
            "\n".join(f"- {p.title}: {p.relevance}" for p in case.allowed_proof) or "(none)"
        )
        verdict = await judge_pitch(
            subject=case.subject,
            body=case.body,
            brand_voice=AGENCY_VOICE,
            allowed_proof_points=allowed_text,
        )
        ok = verdict.passed == case.expected_pass
        agree += ok
        rows.append(
            f"    {case.id:<16} judge_pass={verdict.passed!s:<5} exp={case.expected_pass!s:<5} "
            f"fabricated={verdict.fabricated_proof!s:<5} {'ok' if ok else 'MISS'}"
        )
    return agree / len(CALIBRATION_CASES), rows


async def main() -> None:
    settings = get_settings()
    print(f"Models — qualify: {settings.model_qualify}\n         draft:   {settings.model_draft}")
    print(f"         judge:   {settings.judge_model} (distinct from task models)\n")

    qual_acc, qual_rows = await eval_qualification()
    print(f"[1] Qualification accuracy: {qual_acc:.2f}")
    print("\n".join(qual_rows))

    print("\n[2] Retrieval precision (objective):")
    print("\n".join(await eval_retrieval()))

    print("\n[3] Pitch quality + citation integrity:")
    print("\n".join(await eval_pitches()))

    calib_acc, calib_rows = await eval_judge_calibration()
    print(f"\n[4] Judge calibration vs human labels: {calib_acc:.2f}")
    print("\n".join(calib_rows))


if __name__ == "__main__":
    asyncio.run(main())
