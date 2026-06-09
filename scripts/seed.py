"""Seed the stores (Plane 2 SQLite + Plane 3 Chroma) from a data directory.

uv run python scripts/seed.py --from data/mock        # demo
uv run python scripts/seed.py --from data/<agency>     # any agency, app unchanged
uv run python scripts/seed.py --from data/mock --no-vectors   # SQLite only
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.ingestion import ingest  # noqa: E402


async def _run(data_dir: Path, with_vectors: bool) -> None:
    counts = await ingest(data_dir, with_vectors=with_vectors)
    print(f"Seeded from {data_dir}:")
    for key, value in counts.items():
        print(f"  {key:>22}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Marquee stores from a data directory.")
    parser.add_argument("--from", dest="src", required=True, help="data directory, e.g. data/mock")
    parser.add_argument("--no-vectors", action="store_true", help="skip Chroma seeding")
    args = parser.parse_args()
    data_dir = ROOT / args.src
    if not data_dir.exists():
        raise SystemExit(f"data dir not found: {data_dir}")
    asyncio.run(_run(data_dir, not args.no_vectors))


if __name__ == "__main__":
    main()
