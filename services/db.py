"""Plane 2 — system of record. SQLModel tables + async engine/session."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import JSON, Column
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from config import get_settings


class AgencyRow(SQLModel, table=True):
    __tablename__ = "agency"
    id: str = Field(primary_key=True)
    name: str
    tagline: str
    brand_voice: str


class TalentRow(SQLModel, table=True):
    __tablename__ = "talent"
    id: str = Field(primary_key=True)
    name: str
    category: str
    bio: str
    angle: str
    interests: list[str] = Field(sa_column=Column(JSON))
    values: list[str] = Field(sa_column=Column(JSON))
    tags: list[str] = Field(sa_column=Column(JSON))


class TalentWorkRow(SQLModel, table=True):
    __tablename__ = "talent_work"
    id: str = Field(primary_key=True)
    talent_id: str = Field(foreign_key="talent.id", index=True)
    title: str
    year: int
    kind: str
    description: str
    tags: list[str] = Field(sa_column=Column(JSON))


class BrandRow(SQLModel, table=True):
    __tablename__ = "brand"
    id: str = Field(primary_key=True)
    name: str
    industry: str
    pillars: list[str] = Field(sa_column=Column(JSON))
    notes: str = ""


class ContactRow(SQLModel, table=True):
    __tablename__ = "contact"
    id: str = Field(primary_key=True)
    brand_id: str = Field(foreign_key="brand.id", index=True)
    name: str
    title: str
    role_type: str
    email: str


class PastPitchRow(SQLModel, table=True):
    __tablename__ = "past_pitch"
    id: str = Field(primary_key=True)
    brand_name: str
    brand_industry: str
    talent_name: str
    angle: str
    subject: str
    body: str
    outcome: str


_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().async_db_url)
    return _engine


async def reset_db() -> None:
    """Drop and recreate all tables — used when (re)seeding a single-tenant deploy."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    factory = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        yield session
