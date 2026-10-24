# REPORT: HOW_TO_COLLECT_GARBAGE.md
**Path:** `/home/dylanmccapes/dev/PORTAL_VISION_LUCIFER/game_plans/HOW_TO_COLLECT_GARBAGE.md`
**Scored by:** Composer sub-agent
**Date:** 2026-10-24

## Axis Scores
| Axis | Score | Justification |
|---|---|---|
| Operational Fidelity | 6/10 | It names real levers (venv isolation, `run_tm_wmm_analysis.sh`, `log_eviction`, external_storage) but stops short of a single executable checklist an operator can run without chasing references. |
| Specificity | 7/10 | File paths, functions, venv names, and failure modes (OOM, Killed: 9) are concrete, yet decay thresholds and char-budget numbers stay delegated to `chat_graph.py`. |
| Originality of Aperture | 9/10 | The conscious-eviction / eviction-notice / external-storage frame against ARC, Android GC, and Python is a distinct epistemic lens, not a generic cleanup doc. |
| Compression | 8/10 | Platform survey and alignment tables carry weight without much repetition; only the Agent 11 meta block reads as placement overhead. |
| Navigability | 8/10 | Numbered sections, comparison tables, and a clear §3 philosophy block make the operative passages easy to jump to. |
| **TOTAL** | **38/50** | |

## Strongest Contribution
The PortalVision-vs-runtime-GC alignment table turns “forgetting is first-class” into a comparable policy model (who decides, notice, destination, decay).

## What Is Missing
A bounded operator sequence—when to evict, which tool to invoke, and what receipt to leave—with numeric thresholds pulled from the cited code.

## Brief Summary
The document is a game-plan essay that maps familiar memory-management models (iOS ARC, Android GC, C, Python) onto PortalVision lifecycle practice, with a concrete Python/WMM crash story (shared venv, process OOM) as the stress case. Its operative thesis is pruning over erasure: evict by decay and budget, log to `evictions.jsonl`, and move heavy payload to external storage with pointers left in-repo. Readers leave with philosophy and pointers to scripts and modules rather than one self-contained runbook.
