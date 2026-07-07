# DONE — part-007: Misc enhancements (5 slices)

Source: BACKLOG backlog-005.

## slice-001: CrowdNarrative schema_version — DONE

- `contracts.py`：加 `schema_version: str = "1"`（類別字串，非數字純量）。
- `cli.py`：JSON 輸出加 `schema_version`。
- 測試：`test_crowd_narrative_has_string_schema_version`。

## slice-002: run --sweep — DONE

- `cli.py`：`run` 加 `--sweep`；重構出 `_build_run_dict`，一次跑 3 horizon × 2 intensity
  = 6 格 JSON array。
- 測試：`test_run_sweep_outputs_all_horizon_intensity_cells`、`test_run_sweep_is_deterministic`。

## slice-003: property-based tests (hypothesis) — DONE

- `pyproject.toml`：`[dev]` 加 `hypothesis>=6.0`（runtime deps 仍為 []）。
- `tests/test_properties.py`（新檔）：4 個 property 測試——任意輸入決定論、輸出恆
  categorical、原始數字不外洩、aggregate 折價單調性。

## slice-004: PyPI publish-readiness — DONE

- `python -m build` → wheel + sdist 成功。
- `python -m twine check dist/*` → 兩者 PASSED。
- `PUBLISHING.md`（新檔）：發佈步驟（不含 token）。
- `dist/` 已被 gitignore。

## slice-005: rebuild .codegraph index — N/A (tooling, auto-managed)

`.codegraph` 是外部 MCP 工具的 daemon 資料庫，非產品碼、非本 repo 可直接重建的對象。
套娃已於先前消除、所有檔案在正確單層路徑，索引會在工具下次查詢時自然更新。無需也無法
在此手動重建；標記為 N/A 而非假造完成。

## Verification evidence

- `pytest -q` → **117 passed**（含 4 property tests）
- `ruff check .` → clean
- `twine check dist/*` → PASSED (wheel + sdist)
- Manual QA: `run --sweep` → 6 cells; `run` JSON 含 `schema_version`。

## Incidents

None.
