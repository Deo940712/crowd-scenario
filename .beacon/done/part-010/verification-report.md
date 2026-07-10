# Verification Report — part-010

Source: evidence building — three reproducible case studies with honest limitations.

## slice-001: runner + CASE A — PASS
## slice-002: CASE B + CASE C — PASS
## slice-003: README index + sections — PASS

| Target | Command | Result |
| --- | --- | --- |
| Case study tests | `pytest tests/test_case_studies.py -q` | 12 passed |
| Full suite | `pytest -q` | 244 passed |
| Lint | `ruff check .` | All checks passed |
| Reproduce | `python case_studies/report.py A\|B\|C` | deterministic |
| Firewall (no leak) | test_case_narrative_does_not_leak_raw_numbers | pass (all 3) |
| Limitations present | test_case_doc_has_limitations_section | pass (all 3) |
| Doc/code agreement | test_case_conclusion_matches_doc | pass (all 3) |
| Docs encoding | 3 case docs + 2 READMEs + index | no mojibake |
| Wheel exclusion | packages = ["src/crowdscenario"] | case_studies not shipped |

New: `case_studies/{__init__,runner,cases,report}.py`,
`case_studies/case_{a,b,c}_*.md`, `case_studies/README.md`,
`tests/test_case_studies.py`.
Changed: `README.md`, `README.zh-TW.md`, `pyproject.toml` (pytest pythonpath).

---

## PART part-010 — COMPLETE

Three honest, reproducible case studies ship — the engine now has evidence, not just
features. CASE B/C also demonstrate the 0.2.0 default migration in action.
- `pytest -q` → 244 passed
- `ruff check .` → clean
