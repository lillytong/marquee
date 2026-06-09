# Evals

Evals measure **quality**, not correctness (`tests/` covers correctness). They make real LLM
calls, are non-deterministic, and are **never run in CI** (cost + variance).

## Run
```
uv run python scripts/seed.py --from data/mock   # retrieval evals need seeded stores
uv run python evals/run_evals.py
```

## What it measures
1. **Qualification accuracy** — the qualify model vs. hand-labeled fit/no-fit cases (objective).
2. **Retrieval precision** — experiential **winners-only** (the policy guarantee) + proof-point
   **talent-scoping** and **theme relevance** (objective; no judge).
3. **Pitch quality + citation integrity** — generated drafts scored by an LLM judge, plus an
   objective check that no draft cites a proof id it was not given (the anti-hallucination guardrail).
4. **Judge calibration** — the judge's pass/fail vs. human labels on a fixed set, so the judge is
   trusted only to the degree it agrees with us.

## The judge
The pitch-quality judge uses `config.judge_model` — deliberately a **different, stronger** model
than the task models, to avoid self-preference bias. It is validated by [4] before its scores are
trusted. Objective evals ([1], [2], and the citation check in [3]) use no judge at all.

## Honest caveats
- Labels are **synthetic** — they measure consistency with our stated intent, not absolute truth.
  Real deployment would label on the agency's actual reply/booking outcomes.
- The judge is an LLM; [4] exists precisely because an uncalibrated judge is theater.

## LangSmith
Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `.env`; every eval call is then traced to
LangSmith for inspection. Promoting these datasets + evaluators to LangSmith `evaluate()`
experiments (versioned datasets, run-over-run regression) reuses the functions in this folder and
is the natural next step once an account is connected.
