"""Local embeddings via fastembed — no API key. Sync model wrapped at an executor boundary."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from fastembed import TextEmbedding

from config import get_settings

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=get_settings().embedding_model)
    return _model


def embed_sync(texts: Sequence[str]) -> list[list[float]]:
    return [vec.tolist() for vec in _get_model().embed(list(texts))]


async def embed(texts: Sequence[str]) -> list[list[float]]:
    return await asyncio.to_thread(embed_sync, texts)
