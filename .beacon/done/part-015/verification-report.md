# part-015 Verification Report — De-finance (naming / defaults / docs)

## Outcome

All four slices complete. The engine no longer *presents* as a stock tool — the scenario
parameter is domain-neutral, the persona register and intensity wording are pack-owned,
and the docs lead with a non-finance domain — while every behaviour and emitted output
stayed byte-identical (proven against the part-014 baselines).

## Verification Evidence

UnitTestCore command: `pytest -q` (+ per-slice targets in manifest.json)

Automated commands:
- `pytest -q` → 335 passed (316 baseline + 19 new: 8 seed-alias, 8 pack-field, 3 engine-override)
- `ruff check .` → All checks passed
- `python -O -m pytest -q` → 335 passed (guards survive optimize mode)
- `lsp_diagnostics(src/)` → 0 diagnostics
- `verify` stock_tw + software_migration → full_artifact_stable=True → OK

DETERMINISM (the load-bearing gate, checked after EACH code slice and at the end):
- Three-domain `run` byte-compared vs `.omo/evidence/baseline-*.json` (part-014 era):
  stock_tw / product_launch / software_migration all IDENTICAL at C1, C2, and final.

Deprecation path: `market_scenario_label=` still works and emits DeprecationWarning
(verified in a fresh process; conflicting values raise TypeError).

## What changed

- slice-001 (seed.py): `scenario_label` preferred (3rd positional slot unchanged);
  `market_scenario_label` a keyword-only deprecated alias; internal callers migrated
  (cli.py, examples/real_data.py). ScenarioSeed FIELD name unchanged (schema stability).
- slice-002 (domains/base.py + engine.py): `register` + `intensity_display` are now
  overridable pack fields (validated + deep-frozen); engine reads them instead of
  hardcoding "zh-TW" / 溫和/劇烈; defaults reproduce the old values exactly.
- slice-003 (docs): READMEs (en+zh) lead with software_migration; `scenario_label` in
  all examples; shared-core docstrings domain-neutralized.
- slice-004: this verification + archive.

## Scope fidelity

Product code touched ONLY: seed.py, cli.py (param name at 2 call sites), engine.py
(2 lines), domains/base.py, contracts.py (docstrings only), examples/real_data.py
(param name). Tests touched: test_seed.py (new), test_contracts.py, test_engine.py.
Three shipped packs untouched. No emitted schema change.

## Commits

- chore(beacon): open part-015 de-finance
- refactor(seed): prefer scenario_label, deprecate market_scenario_label alias
- chore(beacon): close part-015 slice-001 (determinism identical)
- feat(domains): add pack-overridable register and intensity_display
- refactor(engine): source register and intensity words from the pack
- chore(beacon): close part-015 slice-002 (determinism identical)
- docs(readme): lead with a non-finance domain example (en+zh)
- docs: neutralize finance-only wording in shared-core docstrings
- chore(beacon): close part-015 slice-003 (docs de-financed)
- (slice-004 close commit follows)

Incidents: none
