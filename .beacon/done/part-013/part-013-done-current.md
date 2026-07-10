# DONE — part-013: Evidence-gated default migration → aggregate_neutral (0.2.0)

Gate (part-008 recommendation) SATISFIED → executed the migration.

## slice-001: gate check + migration impact — DONE

- `.beacon/done/part-013/migration-impact.md`: gate three-conditions verified; dry-run
  (temporarily flipping the default) measured **exactly 3 drifting tests / 232** — small
  blast radius because most tests assert properties, not a specific default value.

## slice-002: execute migration — DONE

- `engine.py`: `run_scenario(..., consensus_mode="aggregate_neutral")` (was `"hashed"`)
  + docstring updated (default since 0.2.0; hashed/aggregate now explicit options).
- `cli.py`: `--consensus-mode` default → `aggregate_neutral` + help updated.
- Test migration (measured values, no hacks):
  - `test_hashed_mode_is_the_default_and_unchanged` → `test_default_mode_is_aggregate_neutral`.
  - `test_default_is_hashed_pinned` → `test_default_is_aggregate_neutral_pinned`.
  - `test_hashed_stock_consensus_pinned`: now passes explicit `consensus_mode="hashed"`.
  - `test_intraday_and_long_leads_are_pinned` / `test_swing_lead_is_roster_first_mover`:
    pinned to explicit hashed (they test chain ordering, captured under hashed).
  - `test_run_defaults_to_hashed_mode` → `test_run_defaults_to_aggregate_neutral_mode`.
- Docs/version: README (en+zh) default wording; `CHANGELOG.md` (0.2.0 behavior change);
  version bump `0.1.0` → `0.2.0` (pyproject + `__version__`).

## Nothing removed

`hashed` and `aggregate` remain explicit options. Firewall guarantees and artifact shape
unchanged. `hashed` golden values are preserved via explicit-mode tests.

## Verification evidence

- `pytest -q` → **232 passed** (test count unchanged; migrated, not added net)
- `ruff check .` → clean
- `python -O` contract → enforced
- CLI: default → `aggregate_neutral`; explicit `--consensus-mode hashed` still works
- `crowdscenario.__version__` → `0.2.0`
- CJK: README.md / README.zh-TW.md / CHANGELOG.md → no mojibake

## Incidents

None. (Migration order chosen safe: added explicit hashed to golden tests BEFORE flipping
the default, so no test was ever left asserting a stale default.)
