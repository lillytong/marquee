# Marquee — Project Rules

Extends `/Users/lillytong/Documents/AI/CLAUDE.md`. Only Marquee-specific additions and the
deviations that file's override scope permits are listed here.

## What this project is
SDR-in-a-box for **one solo talent-management agency** (single-tenant). See `README.md` for the
canonical architecture and `PROJECT_SPEC.md` for the decision log.

## Deviations from the parent standards (within allowed override scope)
- **No `tools/` yet, no `api/` yet, no `memory/` episodic layer.** Phase 1 is the core graph
  through send (dry-run). `api/` arrives in Phase 3, the follow-up cadence in Phase 2.
- **LLM abstraction:** the parent mandates a LiteLLM wrapper in `services/`. Honored via
  `langchain-litellm` (`ChatLiteLLM`) in `services/llm.py`, so it is LiteLLM-backed *and*
  LangGraph-native. Model ids are config-driven, per task — never hardcoded in nodes.

## Hard rules specific to Marquee
- **Data is never hardcoded.** Application code (`agents/`, `prompts/`, business logic in
  `services/`) reads only through repositories (`services/repositories.py`) and memory
  (`memory/`). Raw data files (`data/*`) are read **only** by `services/ingestion.py` and
  `scripts/`. Mock data is one seed; a real agency swaps it by seeding a different directory.
- **Model selection is config-driven and per task.** `config/settings.py` holds a model-per-task
  table + a separate `judge_model` for evals. Swapping provider = config change.
- **Eval judge ≠ task model.** The LLM-as-judge model is configured separately and calibrated
  against human labels. Objective evals (qualification, retrieval) compare to ground truth, no
  judge.
- **Anti-hallucination guardrail:** the drafter may cite only retrieved proof-points, never
  invented past work; the critique node enforces it.

## Run commands
- Install: `uv sync`
- Generate mock data (deterministic, no API key): `uv run python scripts/generate_mock.py`
- Seed the stores: `uv run python scripts/seed.py --from data/mock`
- Lint / types / tests: `uv run ruff check .` · `uv run mypy .` · `uv run pytest`
