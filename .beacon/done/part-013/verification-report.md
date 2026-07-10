# Verification Report — part-013

Source: part-008 recommendation (adopt aggregate_neutral). Gate SATISFIED; executed.

## slice-001: gate check + migration impact — PASS
## slice-002: execute default migration — PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 232 passed |
| Lint | `ruff check .` | All checks passed |
| Firewall under -O | `python -O` contract smoke | enforced |
| CLI default | `run --symbol 0056 --scenario 0056_cut` | consensus_mode=aggregate_neutral |
| Explicit hashed still works | `run ... --consensus-mode hashed` | consensus_mode=hashed |
| Version | `crowdscenario.__version__` | 0.2.0 |
| Docs encoding | README.md / README.zh-TW.md / CHANGELOG.md | no mojibake |

Changed: `engine.py`, `cli.py`, `tests/test_engine.py`, `tests/test_cli.py`,
`README.md`, `README.zh-TW.md`, `pyproject.toml`, `src/crowdscenario/__init__.py`.
New: `CHANGELOG.md`, `.beacon/done/part-013/migration-impact.md`.

## Behavior change (0.2.0)

Default `consensus_mode`: `hashed` → `aggregate_neutral`. Explicit `hashed`/`aggregate`
retained. Callers wanting the old default must pass `consensus_mode="hashed"`.

---

## PART part-013 — COMPLETE

The default consensus model is now the evidence-recommended `aggregate_neutral`, executed
under a satisfied gate with a measured, minimal-drift migration.
- `pytest -q` → 232 passed
- `ruff check .` → clean
- version 0.2.0
