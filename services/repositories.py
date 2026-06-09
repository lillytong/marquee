"""Repositories — the ONLY read path the application uses for Plane 2.

Application code (nodes, business logic) never touches `data/*` or raw tables; it calls these.
Returns domain models, not ORM rows.
"""

from __future__ import annotations

from sqlmodel import select

from models.domain import (
    AgencyProfile,
    Brand,
    Contact,
    PastPitch,
    RoleType,
    Talent,
    TalentWork,
)
from services import db


async def get_agency() -> AgencyProfile | None:
    async with db.session_scope() as s:
        row = (await s.exec(select(db.AgencyRow))).first()
        if row is None:
            return None
        return AgencyProfile(
            id=row.id, name=row.name, tagline=row.tagline, brand_voice=row.brand_voice
        )


async def list_talents() -> list[Talent]:
    async with db.session_scope() as s:
        talent_rows = (await s.exec(select(db.TalentRow))).all()
        work_rows = (await s.exec(select(db.TalentWorkRow))).all()

    works_by_talent: dict[str, list[TalentWork]] = {}
    for w in work_rows:
        works_by_talent.setdefault(w.talent_id, []).append(
            TalentWork(
                id=w.id,
                title=w.title,
                year=w.year,
                kind=w.kind,
                description=w.description,
                tags=w.tags,
            )
        )
    return [
        Talent(
            id=t.id,
            name=t.name,
            category=t.category,
            bio=t.bio,
            angle=t.angle,
            interests=t.interests,
            values=t.values,
            tags=t.tags,
            works=works_by_talent.get(t.id, []),
        )
        for t in talent_rows
    ]


async def get_brand(brand_id: str) -> Brand | None:
    async with db.session_scope() as s:
        row = await s.get(db.BrandRow, brand_id)
        if row is None:
            return None
        return Brand(
            id=row.id, name=row.name, industry=row.industry, pillars=row.pillars, notes=row.notes
        )


async def list_brands() -> list[Brand]:
    async with db.session_scope() as s:
        rows = (await s.exec(select(db.BrandRow))).all()
    return [
        Brand(id=r.id, name=r.name, industry=r.industry, pillars=r.pillars, notes=r.notes)
        for r in rows
    ]


async def get_contact(contact_id: str) -> Contact | None:
    async with db.session_scope() as s:
        row = await s.get(db.ContactRow, contact_id)
        if row is None:
            return None
        return Contact(
            id=row.id,
            brand_id=row.brand_id,
            name=row.name,
            title=row.title,
            role_type=RoleType(row.role_type),
            email=row.email,
        )


async def list_contacts() -> list[Contact]:
    async with db.session_scope() as s:
        rows = (await s.exec(select(db.ContactRow))).all()
    return [
        Contact(
            id=r.id,
            brand_id=r.brand_id,
            name=r.name,
            title=r.title,
            role_type=RoleType(r.role_type),
            email=r.email,
        )
        for r in rows
    ]


async def list_past_pitches() -> list[PastPitch]:
    async with db.session_scope() as s:
        rows = (await s.exec(select(db.PastPitchRow))).all()
    return [
        PastPitch(
            id=r.id,
            brand_name=r.brand_name,
            brand_industry=r.brand_industry,
            talent_name=r.talent_name,
            angle=r.angle,
            subject=r.subject,
            body=r.body,
            outcome=r.outcome,
        )
        for r in rows
    ]
