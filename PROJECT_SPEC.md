# Marquee — Decision Log

> The **[README](./README.md) is the canonical architecture.** This file records *why* the
> key decisions were made, so we don't relitigate them. When the two disagree, the README wins
> and this log should be updated.

**Owner:** Lilly Tong
**Purpose:** portfolio repo demonstrating applied LangChain / LangGraph / LangSmith for FDE /
AI Solutions Engineer roles (RevOps / GTM AI vertical). Productized generalization of a
bespoke outreach pipeline shipped for a private talent-agency client.

**Scope:** SDR-in-a-box for **one solo talent-management agency** — sources brand-side
decision-makers, drafts personalized pitches introducing a roster talent for events/collabs,
runs a human-approved multi-touch follow-up cadence that learns from outcomes.

---

## Decisions & rationale

**LangGraph — scoped, not gratuitous.** Used only where state is genuinely cyclic, durable, or
human-gated: the critique→revise loop, the approval interrupt, and the multi-week follow-up
cadence. The linear research path is plain LCEL. Wrapping a chain in a graph is an anti-pattern;
demonstrating *where not to use it* is part of the point.

**One thread per opportunity** (per pitch), not per campaign. Each pitch is an independent,
resumable state machine so many leads sit at different stages at once without blocking.

**Single-tenant, by choice.** The product is one founder. No `agency_id` plumbing — fake
multi-tenancy (a column without auth/credential isolation) would look prod-ready without being
so. Honest single-tenant now; documented as a future extension.

**Three data planes, never conflated.** (1) Graph execution state — checkpointer; (2) System of
record — SQLite→Postgres, incl. account memory + a running per-brand brief; (3) Vector memory —
experiential (past pitches+outcomes) and talent archives.

**RAG only where the corpus is large *and* the match is fuzzy.** Two justified uses:
- *#1 Experiential memory* (anchor, mandatory): retrieve similar **winning** past pitches as
  few-shot grounding. Corpus grows unbounded; "similar situation" is fuzzy. Cold-start solved
  by seeding the founder's landed pitches at onboarding.
- *#2 Talent proof-points* (supplementary): retrieve the chosen talent's specific past work
  that proves the angle. Big + fuzzy when talent archives are deep.

**Deliberately NOT RAG:**
- *Talent selection* — 50 compact bios fit in context; in-context ranking on two fit signals
  (*demonstrated* + *affinity*). Affinity-only fits must survive (an eco-ambassador with no
  matching project is still a great fit), so selection never runs on retrieval.
- *Account history* — exact `brand_id` lookup; freeform off-platform notes are structured at
  ingest by the LLM (BCC/forward/quick-note) into a running account brief, not RAG-over-mess.
- *Brand research* — done live, just-in-time; never cached/indexed (brand facts go stale).
- *#4 brand-research RAG* — **dropped** for the staleness reason above.

**select-then-prove ordering.** Select the talent (in-context, all 50) → *then* retrieve
proof-points scoped to that talent. #2 degrades gracefully: evidence-backed pitch if proof
exists, affinity pitch if not. Anti-hallucination guardrail: cite only retrieved proof, never
invent past work; the critique node enforces it.

**Negotiation out of scope (#3 dropped from core).** The reply node triages and escalates at
"they're interested"; it does not negotiate rates/terms. A downstream deal-desk / objection
agent (its own contract/rate KB — the kind of legal agent already proven at Planetary) can
attach at the reply node later. Kept separate to avoid a high-stakes commercial-legal surface
on the outreach core.

**Magic-link approval, not reply-parsing.** Deterministic one-click actions for irreversible
outbound; NL "approve 1, 3" parsing is a foot-gun. (Phase 1 uses the `langgraph dev` interrupt;
the magic-link UI lands in Phase 3.)

**Lead source: Apify** (LinkedIn), a deliberate cost tradeoff — target founders can't afford
Apollo (the reason this tool exists). ToS/fragility/coverage risks documented; email
verification needed before send.

**Evals, not just a demo.** LangSmith harness: qualification accuracy vs. labeled fit/no-fit,
pitch-quality LLM-judge (calibrated to human labels), retrieval relevance; human approve/reject
logged as a feedback signal.

---

## Open questions
- Embedding model for the vector store (local sentence-transformers vs. hosted API).
- Reply detection mechanism in prod: Gmail push (Pub/Sub) vs. polling.
- Mock-data generation approach + how real founders upload roster/archives.
