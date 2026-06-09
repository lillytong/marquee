"""Plane 3 — vector store plumbing (Chroma + local fastembed). Policy lives in memory/."""

from __future__ import annotations

import asyncio
from typing import Any

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from config import get_settings
from services.embeddings import embed_sync

EXPERIENTIAL = "experiential"
TALENT_ARCHIVE = "talent_archive"


class _FastEmbedFunction(EmbeddingFunction[Documents]):
    def __call__(self, input: Documents) -> Embeddings:
        return embed_sync(list(input))  # type: ignore[return-value]


_client: ClientAPI | None = None


def _get_client() -> ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=get_settings().chroma_dir)
    return _client


def _get_collection(name: str) -> Collection:
    return _get_client().get_or_create_collection(
        name,
        embedding_function=_FastEmbedFunction(),  # type: ignore[arg-type]
    )


def _reset_sync(name: str) -> None:
    client = _get_client()
    try:
        client.delete_collection(name)
    except Exception:  # noqa: BLE001 — collection may not exist yet
        pass
    client.get_or_create_collection(
        name,
        embedding_function=_FastEmbedFunction(),  # type: ignore[arg-type]
    )


def _add_sync(
    name: str, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]]
) -> None:
    _get_collection(name).add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,  # type: ignore[arg-type]
    )


def _query_sync(
    name: str, query_text: str, k: int, where: dict[str, Any] | None
) -> list[dict[str, Any]]:
    res = _get_collection(name).query(query_texts=[query_text], n_results=k, where=where)
    ids = res["ids"][0]
    docs = (res["documents"] or [[]])[0]
    metas = (res["metadatas"] or [[]])[0]
    dists = (res["distances"] or [[]])[0]
    return [
        {"id": ids[i], "document": docs[i], "metadata": metas[i], "distance": dists[i]}
        for i in range(len(ids))
    ]


def _count_sync(name: str) -> int:
    return _get_collection(name).count()


async def reset(name: str) -> None:
    await asyncio.to_thread(_reset_sync, name)


async def add(
    name: str, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]]
) -> None:
    await asyncio.to_thread(_add_sync, name, ids, documents, metadatas)


async def query(
    name: str, query_text: str, k: int = 3, where: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(_query_sync, name, query_text, k, where)


async def count(name: str) -> int:
    return await asyncio.to_thread(_count_sync, name)
