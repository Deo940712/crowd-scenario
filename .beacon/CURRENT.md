# CURRENT

Status: planning-only

No active executable SLICE is promoted yet.

**part-014 (Structural Firewall Hardening) COMPLETE** — all 4 slices done, archived under
`.beacon/done/part-014/`:
- slice-001 contracts.py: ScenarioSeed ordinal-string validation, PersonaReaction
  validation, synthetic_population hard-wired
- slice-002 domains/base.py: finite-only numerics, voice_variants stance bound,
  DomainPack deep-freeze (determinism byte-identical)
- slice-003 cli.py + composer.py: --metrics finite validation, compose_divergence
  ContractError guard
- slice-004: full verification + README claim calibration (no doc edit needed)

Final: `pytest -q` → 316 passed (was 262 baseline), ruff clean, `python -O` 316,
LSP 0 diagnostics, three-domain determinism byte-identical. Version unchanged (0.2.0).

See `.beacon/done/part-014/verification-report.md`.

## Open backlog (need DESIGN + TODO before promotion)

- backlog-007 (pack prior consensus model) — WON'T-DO unless a future domain over-neutralizes.
- backlog-008 (report divergence panel + `--all-cases` batch) — enhancement.

No open executable work. New requests need a fresh PART DESIGN + TODO.
