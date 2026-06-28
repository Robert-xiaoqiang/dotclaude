# Skill: agent-memory-architecture

## Purpose
Design or review a **hierarchical, self-evolving agent-memory framework** — the
architecture pattern behind MemCodex. Captures the load-bearing decisions
(representation layers, provenance, coarse-to-fine retrieval, the three planes,
self-evolution, and the production engineering of config/logging/events/async/
safety) distilled from a survey of ~20 memory systems (Mem0, MemOS, Letta, Zep/
Graphiti, Cognee, LangGraph/LangMem, A-MEM, Generative Agents, Voyager, …) plus
the cognitive-science of consolidation.

## When to Use
- Designing an LLM-agent memory system, or adding memory to an agent
- Reviewing a memory/RAG design ("is this the right structure?")
- The user mentions: layered memory, self-evolving/self-organizing memory,
  coarse-to-fine retrieval, provenance, forgetting/consolidation, memory governance
- Choosing config/logging/event/async/safety machinery for such a system

## Core architecture principles
1. **Layer by *representation*, not just granularity.** Keep distinct *kinds* of
   memory, coarse→fine: `skill` (procedures) → `graph` (entity/relation facts) →
   `summary` (compressed episodes) → `verbatim` (raw turns; the only ground truth)
   → `working` (ephemeral). Map to cognition: episodic / semantic / procedural.
2. **Verbatim is the immutable floor.** Everything else is *derived*. Never mutate
   or delete ground truth; derived layers may evolve.
3. **Provenance via leaf-support.** Every item carries `support` = the transitive
   set of verbatim-leaf ids it rests on. This gives (a) lossless recovery and
   (b) **provenance-guided descent**: a trusted coarse hit narrows the next
   layer's search to its own evidence sub-tree (follow the citation), instead of
   re-running similarity search (which can fetch a similar-but-wrong passage).
4. **Coarse-to-fine, confidence-gated descent.** Try the coarsest layer; stop if
   the top hit clears a threshold τ; else descend. `require_evidence` forces
   descent to verbatim. The traversal trace IS the audit artifact.
5. **Event-driven updates.** Typed events trigger different transforms:
   turn/tool/observation → append verbatim; segment/task boundary → summarize then
   graph-extract; success/failure/reflection → distil a skill.

## The three planes (this is what makes it *self-evolving*)
Think network reference model: a layered **data plane** + an adaptive **control
plane** + an off-path **management plane**. Keep evolution **opt-in & deterministic**.
- **Data plane** — the representation layers above.
- **Control plane** — learns from the *query stream*. (a) *Crystallize* recurring
  deep descents (same intent signature) into skill items keyed by intent, so the
  same query class resolves coarse next time. (b) *Adaptive routing*: raise a
  class's τ after a wrong coarse stop. Teach it post-answer: `learn(trace, success)`.
- **Management plane** — the "nighttime" pass, off the read path. `heat` =
  frequency + evidence-mass + recency (promote hot, decay cold). **Consolidation
  re-derives summaries from their verbatim leaves, never from the prior summary**
  (the drift / reconsolidation-corruption guard), behind a write-validation gate,
  then **supersedes** drifted items bi-temporally (`invalid_at`/`supersedes`) —
  never deletes.

## Self-evolving design rules
- **Signals that trigger reorganization:** access frequency/recency (heat),
  retrieval-sufficiency, answer success/failure, query-distribution repetition,
  contradictions.
- **Reorganizations:** promote/crystallize detail into reusable forms; merge/
  generalize/dedup; form links / re-cluster; decay/forget derived items; resolve
  contradictions by *supersede*; re-tune routing weights.
- **Keep it safe + auditable:** never mutate ground truth; supersede-don't-delete
  (bi-temporal, reversible); provenance everywhere; a write-validation gate
  rejecting derivations that contradict core facts; re-derive from leaves to bound
  drift to O(window); run contradiction detection *before* dedup (else
  contradictions get dropped as near-duplicates).

## Production engineering patterns
- **Config:** pydantic v2 models with `extra='forbid'` (typos fail loudly) as the
  typed contract; a `core` group owns paths/log/seed and backends read from it;
  compose per-concern groups (`core/memory/agent/gym`) via includes; pick backends
  through name→builder **registries** (not `if/else`). Hydra/OmegaConf optional for
  group composition + multirun (compose → `to_container(resolve=True)` → validate).
- **Logging:** structured (JSON or console) with `run_id/session_id/query_id/layer`
  via **contextvars**; driven by core config; **separate from the audit artifact**
  (logs may carry wall-clock; the audit must stay deterministic). Stdlib `logging`
  is enough; structlog optional.
- **Events / write path:** decouple write-time consolidation from the read path —
  reads answer now, consolidation runs later (scheduler/queue, LangMem-style
  debounced reflection, MemOS-style per-scope queues). Make ingestion idempotent
  (content-hash or `uuid5`), order per session (single-consumer FIFO), retry with
  backoff. Progress: in-process bus + append-only log (as outbox) → Redis Streams →
  task queue.
- **Async:** sync core + `asyncio.to_thread` facade is the cheap async-ready path;
  bound LLM calls with a semaphore; per-key locks serialize same-session writes.
- **Safety:** lossy/destructive ops go through **propose → approve → apply** with
  proposer ≠ approver (two-person control), idempotent apply, dry-run preview;
  prefer soft-archive + version chain over hard delete; refuse to delete ground
  truth. (LangGraph `interrupt()` is the reference HITL mechanism.)
- **Dependency posture:** dep-light core = **stdlib + pydantic**; put Hydra,
  structlog, Redis, queues, async libs, authz behind **optional extras** that plug
  into the same validated boundary.

## Pitfalls (seen in real frameworks)
- Pure verbatim + semantic retrieval can't answer *state* or *procedure* questions
  without re-deriving them every read — add the semantic/skill layers.
- Similarity re-search on descent can retrieve a wrong-but-similar passage — use
  provenance pointers instead.
- Iterative summarization of summaries drifts — always re-derive from leaves.
- Autonomous hard deletes (e.g. LangMem) corrupt silently — gate lossy ops.
- `extra='ignore'` config silently drops typo'd keys — use `forbid`.

## Key references
Survey "Storage→Reflection→Experience" (arXiv:2605.06716); MemOS (2507.03724);
MemoryOS heat (2506.06326); A-MEM (2502.12110); Engram bi-temporal (2606.09900);
Generative Agents (2304.03442); Voyager (2305.16291); Graphiti/Zep (getzep);
LangGraph HITL `interrupt`. Cognitive: complementary learning systems
(Kumaran/Hassabis/McClelland 2016); reconsolidation (PMC5605913).
