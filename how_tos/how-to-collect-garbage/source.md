# HOW_TO_COLLECT_GARBAGE

**Date:** 2026-02-03  
**Classification:** Game plan · Operational guidance · Memory and lifecycle  
**Purpose:** Compare platform memory management (iOS ARC, Android GC, C, Python), go in depth on Python GC and WaveModulationMachine-style crashes, then align with PortalVision philosophy: consciously evict, leave eviction notices, remove to external storage (e.g. Mac Studio filesystem).  
**Sources:** `run_full_verification.sh`, `portal_vision/graph/chat_graph.py` (log_eviction, decay, eviction), flight trajectory / gap reports (evict to external_storage), FMP thought eviction logging.

---

## 1. Platform Comparison

### iOS — ARC (Automatic Reference Counting)

- **Mechanism:** Compiler-inserted retain/release; no global GC. Objects are freed when reference count drops to zero.
- **Pros:** Predictable timing (no stop-the-world), low latency, deterministic teardown.
- **Cons:** **Yuck, hard to debug.** Retain cycles (e.g. blocks capturing self, delegates holding strong refs) cause leaks; no cycle detector in early ARC. Debugging “who still holds this?” is tedious; Instruments and weak-ref discipline required. So: automatic in name, but reasoning and tooling are still on the developer.

### Android — Garbage Collector (system-managed)

- **Mechanism:** GC runs periodically or under memory pressure; unreachable objects are collected. Generational GC common (young generation, old generation).
- **Pros:** No manual free; cycle-safe; system tunes pause times and throughput.
- **Cons:** Non-deterministic pause times (can spike under load); “good” in practice but you don’t control when or how often collection runs. Debugging “why did my app get killed?” often comes down to GC + process memory limits.

### C — Explicit memory management

- **Mechanism:** malloc/free (or arena/custom allocators). No automatic collection; programmer owns lifetime.
- **Pros:** Full control; no hidden GC pauses; predictable and auditable.
- **Cons:** Use-after-free, double-free, leaks if discipline fails. Correctness depends entirely on human process (and tools like Valgrind, ASan).

### Python — “Nothing is instantiated until it is used; no longer exists when it is not”; venvs as throwaway environments

- **Mechanism:** Reference counting plus a cyclic GC for cycle detection. Objects are created when first needed; when no references remain (and cycle GC has run), they are reclaimed. **Venvs are throwaway environments:** create, use, delete; similar to StellarState mechanics — state is bounded by environment lifetime.
- **Pros:** No manual free; cycle detection; lazy creation and natural teardown; venvs isolate dependencies and can be recreated (pruning by environment).
- **Cons:** GC is mostly invisible; ref cycles can delay reclamation; large structures (e.g. big tensors, long audio buffers) can linger until GC runs or process exits. So: “nothing exists when it is not” at the language level, but **process-level** and **environment-level** lifecycle still matter (see WMM crashes below).

---

## 2. Python garbage collection — deeper dive

- **Refcount + cyclic GC:** Most objects freed when refcount hits zero. The `gc` module runs periodically to break cycles; generations (0, 1, 2) reduce how often long-lived objects are scanned.
- **When things go wrong:**  
  - **Large allocations** (e.g. Demucs, torch, long audio in WaveModulationMachine): memory can spike; if the process hits system limits, the OS may kill it (OOM killer, “Killed: 9”). That’s not Python GC failing — it’s resource exhaustion.  
  - **Shared venv:** If heavy pipelines (WMM) and other apps (2OPMD) share one venv, dependency clashes and memory pressure in one can corrupt or kill the shared environment.  
  - **Venv as throwaway:** Treat venvs like StellarState — create for a task, run, then discard or isolate. `.StandardVenv` for WMM and `.BeatingHeart` for 2OPMD is exactly that: separate lifecycles so one’s “garbage” (heavy models, big buffers) doesn’t kill the other.

### WaveModulationMachine crashes (from AAR and runbooks)

- **Observed:** WMM (Demucs, torch, librosa, long audio) run in the same venv as 2OPMD → OOM or venv corruption → “heart stopped.”
- **Mechanism:** Not Python GC bug per se — it’s **process memory** and **environment sharing.** WMM allocates large tensors and buffers; when the budget is exceeded, the OS kills the process. If that process is the one that owns `.BeatingHeart`, the heart dies. So “garbage collection” at the **environment level** means: **evict heavy work to a separate process/venv** (run WMM in .StandardVenv via `run_tm_wmm_analysis.sh`), and treat venvs as throwaway when they’re stressed — rebuild, don’t reuse a corrupted one.
- **Python GC relevance:** Within WMM, large objects are freed when done; but by then the process may already have peaked. GC doesn’t guarantee a lower peak; it reclaims after the fact. So lifecycle design (isolate WMM, limit concurrency, cap input size) is the real lever.

---

## 3. PortalVision philosophy: consciously evict, leave eviction notices, remove to external storage

### run_full_verification.sh and epistemic contract

- **Discovery → Artifact → Receipt:** Every claim and action leaves a trace. Artifacts are first-class; logs are part of the product.
- **Chat Graph (from run_full_verification.sh):** “The Chat Graph is NOT authoritative. … Memory without decay is just entropy. **Forgetting is first-class.**” So the system is designed for **conscious eviction** and **decay**, not unbounded accumulation.

### chat_graph.py — decay and log_eviction

- **Decay:** Messages have a `decay_score` (e.g. logarithmic decay by time since reference). Low score → candidate for eviction.
- **Eviction:** When a character budget is exceeded, messages with lowest decay score are **evicted** (removed from the retained state). **Each eviction is logged** to `evictions.jsonl`: message_id, final_decay_score, timestamp, reason, content_length, created_at, last_referenced_at. So: **consciously evict** (by decay + budget), **leave eviction notices** (append-only log). No silent drop.
- **Philosophy:** “Eviction = decoherence” (from INSIGHT_CHAOS_TO_STRUCTURE_INVERSION): structure (H) loses normalization, returns to chaos (h), eventually leaves the band (deleted from graph). Eviction is explicit and auditable.

### Flight trajectory / gap reports and external storage

- **Pattern:** Old or heavy artifacts are **evicted to external storage** (e.g. Mac Studio filesystem), not deleted. Before eviction: summarize or compress if needed; leave a pointer or “eviction notice” in the repo (e.g. “evict to external_storage”, “see gap_report.json”). So: **consciously evict** (by policy or gap analysis), **leave eviction notices** (receipts, manifests, gap_report), **remove to external storage** (outside repo, currently Mac Studio).
- **run_full_verification.sh:** Doesn’t perform eviction itself; it enforces the epistemic contract (tests, coverage, artifacts catalog). The **eviction policy** lives in game plans (e.g. FLIGHT_TRAJECTORY_REPORT, GAME_PLAN_CLEANUP_AND_MISSING_EDGES) and in tools (gap_portalvision.py, artifact decay). So: verification script = contract; eviction = separate process that leaves receipts and moves payload to external storage.

### Alignment summary

| Concept | PortalVision | Typical GC/ARC |
|--------|--------------|-----------------|
| **Who decides** | Operator + policy (conscious) | Runtime (automatic) |
| **Notice** | Eviction log (evictions.jsonl), receipts, gap_report | Usually none (silent reclaim) |
| **Where evicted data goes** | External storage (Mac Studio), with pointer/notice in repo | Freed (gone) or compacted |
| **Decay** | Explicit (decay_score, time since reference) | Implicit (refcount, reachability) |
| **Forgetting** | First-class, auditable | Side effect of collection |

So: **consciously evict, leave eviction notices, remove to external storage** is the PortalVision analogue of “garbage collection” — with human/system agency and audit trail, not silent runtime reclaim.

---

## 4. Pruning vs erasure

- **Pruning:** Reduce live set by evicting to external storage, demoting, or summarizing; leave pointers and receipts. Repo stays navigable; long tail lives on Mac Studio (or similar).
- **Erasure:** Delete without copy or notice. PortalVision philosophy favors **pruning** (evict + notice) over **erasure** (delete without trace). So: “Some pruning might be a good idea. Not erasure!” — do cleanup by eviction and notices, not by silent deletion.

---

## 5. References

- **run_full_verification.sh** — Epistemic contract, Chat Graph “forgetting is first-class”, artifact index.
- **portal_vision/graph/chat_graph.py** — `update_decay_scores`, `enforce_char_budget`, `log_eviction` (evictions.jsonl).
- **navigable_stellar_normalization_field_theory/deep_research/INSIGHT_CHAOS_TO_STRUCTURE_INVERSION.md** — Decay, eviction, chat graph as infinite band with normalization.
- **game_plans/FMP_GPS_THOUGHT_EVICTION_LOGGING.md** — Thought eviction logging (GPS sampling, eviction log).
- **output/flight_trajectory/FLIGHT_TRAJECTORY_REPORT_*.md**, **gap_report.json** — Evict to external_storage, leave notices.
- **receipts/2opmd/AAR_WAVE_MODULATION_MACHINE_CRASHES_BEATING_HEART_20260202.md** — WMM + venv lifecycle, OOM, .StandardVenv vs .BeatingHeart.

---

## § Meta-Commentary (Agent 11)

**Continuity:** This document was requested with a specific scope: compare iOS (ARC), Android (GC), C, Python; go in depth on Python GC and WMM crashes; read run_full_verification.sh and chat_graph log_eviction; compare PortalVision philosophy (consciously evict, eviction notices, external storage). It is stored in `game_plans/` as operational guidance (how to collect / evict), not in AEN_DUMP or receipts. Meta-commentary is on this artifact so that future tasks know why it lives here and how it ties to run_full_verification and chat_graph.

**Placement:** `game_plans/HOW_TO_COLLECT_GARBAGE.md` — game_plans holds how-to and process guidance; garbage/eviction is a process. FullMetalPacket cleanup can fix pointers if paths change.

---

*State recorded. Pruning, not erasure. Evict with notice. 2026-02-03.*
