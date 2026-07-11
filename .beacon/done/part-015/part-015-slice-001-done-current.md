# DONE — part-015 slice-001: scenario_label rename + alias (seed.py)

Goal SATISFIED — `make_seed` prefers `scenario_label` (3rd positional param unchanged);
`market_scenario_label` remains a deprecated keyword-only alias.

## What was implemented (TDD, plan todos 2-3)

- seed.py signature: `make_seed(symbol, metrics, scenario_label=None, rng_seed=42,
  horizon="swing", intensity="mild", pack=STOCK_TW, *, market_scenario_label=None)` —
  only the alias is keyword-only, so every pre-existing positional/keyword call pattern
  keeps working (verified against 40+ call sites during planning review).
- Alias resolution: both-given-different → TypeError; old-only → DeprecationWarning
  (stacklevel=2) + used; neither → TypeError. ScenarioSeed.market_scenario_label FIELD
  unchanged (schema stability).
- Internal callers moved to the new name: cli.py:138,200; examples/real_data.py:48.
- New tests/test_seed.py: 8 tests (new-name, positional-3rd, alias+warn, no-warn on new
  name, conflict TypeError, same-value allowed, missing TypeError, hash-identical).

## Verification Evidence

UnitTestCore command: `pytest tests/test_seed.py tests/test_contracts.py -q`

Automated commands:
- `pytest tests/test_seed.py -q` → 8 passed (5 observed failing first — TDD red recorded)
- `pytest -q` → 324 passed (316 + 8 new; zero regressions)
- `ruff check .` → All checks passed

DETERMINISM (hard gate): three-domain `run` byte-compared vs part-014 baselines
(`.omo/evidence/baseline-*.json`): stock_tw / product_launch / software_migration all
IDENTICAL (same resolved label string → same hash).

Manual QA: new-name path, old-name warns (DeprecationWarning), conflicting values
TypeError — all recorded in `.omo/evidence/task-2-definance-crowd-scenario.txt`.

Commit: refactor(seed): prefer scenario_label, deprecate market_scenario_label alias

Incidents: none
