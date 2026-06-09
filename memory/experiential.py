"""Experiential memory (#1) — retrieve similar WINNING past pitches as few-shot grounding.

Retrieval policy: pre-filter to winners only, then semantic rank. The corpus grows unbounded
with use; this is the feedback-loop moat.
"""

from __future__ import annotations

from typing import Any

from models.domain import PastPitch
from services import vector_store


class ExperientialMemory:
    @staticmethod
    def _document(pitch: PastPitch) -> str:
        return (
            f"Brand industry: {pitch.brand_industry}. Angle: {pitch.angle}. "
            f"{pitch.subject}\n{pitch.body}"
        )

    async def seed(self, pitches: list[PastPitch]) -> int:
        await vector_store.reset(vector_store.EXPERIENTIAL)
        if not pitches:
            return 0
        await vector_store.add(
            vector_store.EXPERIENTIAL,
            ids=[p.id for p in pitches],
            documents=[self._document(p) for p in pitches],
            metadatas=[
                {
                    "outcome": p.outcome.value,
                    "is_win": p.is_win,
                    "brand_industry": p.brand_industry,
                    "talent_name": p.talent_name,
                    "angle": p.angle,
                    "subject": p.subject,
                    "body": p.body,
                }
                for p in pitches
            ],
        )
        return len(pitches)

    async def retrieve_similar_wins(
        self, *, industry: str, angle: str, k: int = 3
    ) -> list[dict[str, Any]]:
        query = f"Brand industry: {industry}. Angle: {angle}."
        return await vector_store.query(
            vector_store.EXPERIENTIAL, query, k=k, where={"is_win": True}
        )
