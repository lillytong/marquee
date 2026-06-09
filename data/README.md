# Data — the import contract

The application **never** reads these files directly. Only `services/ingestion.py` (and the
`scripts/`) do. Everything in the app reads from the stores (SQLite + Chroma) via repositories.

**Mock data is just one seed.** A real agency uses Marquee by providing their own files in this
same schema and seeding from their own directory:

```
uv run python scripts/seed.py --from data/mock      # the demo
uv run python scripts/seed.py --from data/acme       # a real agency — app unchanged
```

## Files & schema

Each `data/<agency>/` directory contains five JSON files. Shapes are defined and validated by the
Pydantic models in `models/domain.py` (the import DTOs are the same domain models).

| File | Contains | Seeds |
|------|----------|-------|
| `agency.json` | Single agency profile: name, one-line, brand voice guidance | Plane 2 |
| `talents.json` | Roster: each talent's bio (identity + interests/values + **angle**), tags, and a **work archive** (past works) | Plane 2 + Plane 3 (#2) |
| `brands.json` | Target brands: name, industry, **durable pillars** (not time-sensitive events) | Plane 2 |
| `contacts.json` | Brand-side contacts (fictional people, fake emails): name, title, role type, brand ref | Plane 2 |
| `seed_pitches.json` | Past pitches + **outcomes** (booked / meeting / replied / ignored) | Plane 3 (#1) |

## Conventions
- **Fictional people only.** Contacts and talents are invented; emails use `@example.com`.
- **Brands** may use real public brand names (they're pitch *targets*, not personal data).
- **Brand data is durable facts only** (positioning/pillars) — never cached time-sensitive
  events; live brand research happens just-in-time in the graph.
- Regenerate the mock seed deterministically with `scripts/generate_mock.py` (seeded RNG, no LLM
  key required).
