# Verification Report — part-008

Source: consensus-model evaluation (choose default by evidence, not intuition).

## Slices

| Slice | Status | Evidence |
| --- | --- | --- |
| 001 lock current models | DONE | `_EVAL_CASES` golden + default==hashed pin |
| 002 neutral-baseline mode | DONE | engine + CLI + 6 tests (determinism/hash-indep/neutral-stability) |
| 003 comparison matrix | DONE | `tools/eval_consensus.py` + 3 reproducibility tests |
| 004 recommendation | DONE | `consensus-evaluation.md` (5-criteria decision) |

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 232 passed |
| Lint | `ruff check .` | All checks passed |
| Matrix reproducible | `pytest tests/test_consensus_eval.py -q` | 3 passed |
| Matrix output | `PYTHONPATH=src python tools/eval_consensus.py` | deterministic; hash-indep True |

New: `tools/eval_consensus.py`, `tests/test_consensus_eval.py`,
`.beacon/done/part-008/consensus-evaluation.md`.
Changed: `engine.py` (aggregate_neutral mode), `cli.py` (choice), `tests/test_engine.py`.

## Decision & gate

Recommendation: **adopt `aggregate_neutral` as default** (executed under part-013, whose
gate is now SATISFIED). backlog-007 closed as won't-do.

---

## PART part-008 — COMPLETE

Default choice is now evidence-backed, not a guess. Three modes ship; the recommended
default change is queued behind part-013's migration gate.
- `pytest -q` → 232 passed
- `ruff check .` → clean
