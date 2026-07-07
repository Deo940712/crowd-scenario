# Verification Report — part-003

Source: BACKLOG backlog-002 (bug: swing ordering aliases intraday).

## slice-001: Give swing a distinct middle-ground ordering

Date: (current session)
Status: PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 90 passed (84 + 6) |
| Lint | `ruff check .` | All checks passed |
| Manual QA | `run --horizon {intraday,swing,long}` | leads distinct: PTT/Dcard 風向 / 存股族 / 外資視角 |
| Regression (no drift) | pinned intraday+long leads | unchanged (test_intraday_and_long_leads_are_pinned) |

New tests in `tests/test_engine.py`:
- `test_all_three_horizons_lead_with_distinct_personas`
- `test_intraday_and_long_leads_are_pinned`
- `test_swing_lead_is_roster_first_mover`
- `test_each_horizon_reaction_chain_is_deterministic` (×3)

---

## PART part-003 — COMPLETE

Single slice done. swing bug fixed; swing is now a genuine roster-order middle ground.
- `pytest -q` → 90 passed
- `ruff check .` → clean
