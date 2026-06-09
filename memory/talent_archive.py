"""Talent archive (#2) — retrieve a CHOSEN talent's specific works as proof-points.

Scoped to one talent_id (set after selection). Supplementary: may return nothing, in which case
the drafter falls back to affinity. Never used to *select* the talent.
"""

from __future__ import annotations

from typing import Any

from models.domain import Talent
from services import vector_store


class TalentArchive:
    async def seed(self, talents: list[Talent]) -> int:
        await vector_store.reset(vector_store.TALENT_ARCHIVE)
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        for talent in talents:
            for work in talent.works:
                ids.append(work.id)
                documents.append(f"{work.title} ({work.year}, {work.kind}). {work.description}")
                metadatas.append(
                    {
                        "talent_id": talent.id,
                        "title": work.title,
                        "kind": work.kind,
                        "year": work.year,
                        "tags": ", ".join(work.tags),
                    }
                )
        if not ids:
            return 0
        await vector_store.add(vector_store.TALENT_ARCHIVE, ids, documents, metadatas)
        return len(ids)

    async def retrieve_proof_points(
        self, *, talent_id: str, query_text: str, k: int = 3
    ) -> list[dict[str, Any]]:
        return await vector_store.query(
            vector_store.TALENT_ARCHIVE, query_text, k=k, where={"talent_id": talent_id}
        )
