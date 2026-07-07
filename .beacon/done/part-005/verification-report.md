# Verification Report — part-005

Source: BACKLOG backlog-004 (real-data worked example).

## slice-001: Real-data worked example + docs — PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 98 passed (95 + 3) |
| Lint | `ruff check .` | All checks passed |
| Firewall (no leak) | `test_example_does_not_leak_raw_scores` | raw -0.6 / 8.5 absent |
| Determinism | `test_example_is_deterministic` | pass |
| Manual QA | `python examples/real_data.py` | prints consensus + buckets, no raw numbers |

New: `examples/real_data.py`, `tests/test_examples.py`, README "Feeding real data".

---

## PART part-005 — COMPLETE

Users have a runnable, firewall-safe pattern for feeding real data.
- `pytest -q` → 98 passed
- `ruff check .` → clean
