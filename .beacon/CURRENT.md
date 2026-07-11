# CURRENT

Status: planning-only

No active executable SLICE is promoted yet.

**part-015 (De-finance) COMPLETE** — all 4 slices done, archived under
`.beacon/done/part-015/`:
- slice-001 seed.py: scenario_label preferred, market_scenario_label a deprecated
  keyword-only alias (DeprecationWarning; conflict → TypeError)
- slice-002 base.py + engine.py: register + intensity_display are pack-overridable;
  defaults reproduce the old values (three domains byte-identical)
- slice-003 docs: READMEs lead with software_migration; shared-core docstrings
  domain-neutralized
- slice-004: full verification + archive

Final: `pytest -q` → 335 passed (was 316), ruff clean, `python -O` 335, LSP 0,
three-domain determinism byte-identical vs part-014 baselines. Version unchanged (0.2.0).

See `.beacon/done/part-015/verification-report.md`.

## Open backlog (need DESIGN + TODO before promotion)

- backlog-007 (pack prior consensus model) — WON'T-DO unless a future domain over-neutralizes.
- backlog-008 (report divergence panel + `--all-cases` batch) — enhancement.

No open executable work. New requests need a fresh PART DESIGN + TODO.
