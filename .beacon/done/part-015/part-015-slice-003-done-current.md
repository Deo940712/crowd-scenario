# DONE — part-015 slice-003: docs de-finance (READMEs + docstrings)

Goal SATISFIED — the first impression is no longer "a stock tool".

## What was implemented (plan todos 7-8)

- README.md + README.zh-TW.md: CLI and Python sections now LEAD with the
  software_migration domain (breaking v9 rewrite), product launch second, stock third
  (kept, not deleted); `make_seed` examples use `scenario_label`; the remaining
  `market_scenario_label=` occurrences in "Feeding real data" updated too.
- Docstrings neutralized: contracts.py (module + ScenarioSeed: raw metric examples now
  span domains, market_scenario_label documented as historical-for-schema-stability);
  seed.py (bucketing described domain-agnostically); domains/base.py (module docstring
  states the core is domain-agnostic and documents register/intensity_display).

## Verification Evidence

UnitTestCore: design-review gate (docs-only slice, no automated command per manifest).

Automated commands (regression only):
- `pytest -q` → 335 passed (docs changes cannot affect tests — confirmed)
- `ruff check .` → All checks passed

Manual QA:
- item: README lead example runs
- status: passed — CLI `run --domain software_migration --symbol big_rewrite --scenario
  v9_rewrite` exit 0; Python lead example prints `negative`
  (`.omo/evidence/task-7-definance-crowd-scenario.txt`)
- item: no stale `market_scenario_label=` in READMEs
- status: passed (grep clean after edit)

Commits:
- docs(readme): lead with a non-finance domain example (en+zh)
- docs: neutralize finance-only wording in shared-core docstrings

Incidents: none
