"""The ONLY code (besides scripts/) that reads raw data files. Validates → writes to stores.

Mock data and a real agency's data both flow through here. Swapping agencies = a different dir.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memory.experiential import ExperientialMemory
from memory.talent_archive import TalentArchive
from models.domain import AgencyDataset
from services import db


def load_dataset(data_dir: Path) -> AgencyDataset:
    def read(name: str) -> Any:
        return json.loads((data_dir / name).read_text())

    return AgencyDataset(
        agency=read("agency.json"),
        talents=read("talents.json"),
        brands=read("brands.json"),
        contacts=read("contacts.json"),
        seed_pitches=read("seed_pitches.json"),
    )


async def ingest(data_dir: Path, *, with_vectors: bool = True) -> dict[str, int]:
    dataset = load_dataset(data_dir)
    await db.reset_db()

    async with db.session_scope() as s:
        a = dataset.agency
        s.add(db.AgencyRow(id=a.id, name=a.name, tagline=a.tagline, brand_voice=a.brand_voice))
        for t in dataset.talents:
            s.add(
                db.TalentRow(
                    id=t.id,
                    name=t.name,
                    category=t.category,
                    bio=t.bio,
                    angle=t.angle,
                    interests=t.interests,
                    values=t.values,
                    tags=t.tags,
                )
            )
            for w in t.works:
                s.add(
                    db.TalentWorkRow(
                        id=w.id,
                        talent_id=t.id,
                        title=w.title,
                        year=w.year,
                        kind=w.kind,
                        description=w.description,
                        tags=w.tags,
                    )
                )
        for b in dataset.brands:
            s.add(
                db.BrandRow(
                    id=b.id, name=b.name, industry=b.industry, pillars=b.pillars, notes=b.notes
                )
            )
        for c in dataset.contacts:
            s.add(
                db.ContactRow(
                    id=c.id,
                    brand_id=c.brand_id,
                    name=c.name,
                    title=c.title,
                    role_type=c.role_type.value,
                    email=str(c.email),
                )
            )
        for p in dataset.seed_pitches:
            s.add(
                db.PastPitchRow(
                    id=p.id,
                    brand_name=p.brand_name,
                    brand_industry=p.brand_industry,
                    talent_name=p.talent_name,
                    angle=p.angle,
                    subject=p.subject,
                    body=p.body,
                    outcome=p.outcome.value,
                )
            )
        await s.commit()

    counts = {
        "talents": len(dataset.talents),
        "talent_works": sum(len(t.works) for t in dataset.talents),
        "brands": len(dataset.brands),
        "contacts": len(dataset.contacts),
        "seed_pitches": len(dataset.seed_pitches),
    }
    if with_vectors:
        counts["experiential_vectors"] = await ExperientialMemory().seed(dataset.seed_pitches)
        counts["talent_work_vectors"] = await TalentArchive().seed(dataset.talents)
    return counts
