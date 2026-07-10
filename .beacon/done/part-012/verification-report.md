# Verification Report — part-012

Source: third domain pack — proves the engine is not a renamed stock-sentiment model.

## slice-001: SOFTWARE_MIGRATION pack + sanity — PASS
## slice-002: CLI + docs wiring — PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 258 passed |
| Lint | `ruff check .` | All checks passed |
| Pack validity | validate_pack (in __post_init__) | constructs OK |
| Semantic sanity resist | big_rewrite (rewrite/painful/negligible) | negative → resist (net -8) |
| Semantic sanity adopt | smooth_major (minor/automated/substantial) | positive → adopt (net +8) |
| Display vocabulary | test_software_pack_display_vocabulary | resist/wait/adopt |
| CLI | `run --domain software_migration --symbol big_rewrite --scenario v9_rewrite` | domain ok, resist |
| CLI sweep | `... --sweep` | 6 cells, all software_migration |
| Docs encoding | software.py + 2 READMEs | no mojibake |

New: `src/crowdscenario/domains/software.py`.
Changed: `src/crowdscenario/__init__.py`, `cli.py`, `tests/test_engine.py`,
`tests/test_cli.py`, `README.md`, `README.zh-TW.md`.

---

## PART part-012 — COMPLETE

Three domains now ship (stock_tw, product_launch, software_migration). The third — a
non-finance, non-consumer ecosystem domain with resist/wait/adopt vocabulary — is the
clearest proof the engine is genuinely domain-agnostic.
- `pytest -q` → 258 passed
- `ruff check .` → clean
