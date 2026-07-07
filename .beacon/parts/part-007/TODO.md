# part-007 TODO

Design authority: `.beacon/parts/part-007/DESIGN.md`
Source: BACKLOG backlog-005

## SLICE Map

各 slice 獨立、可分別 promote。優先序由使用者決定（PyPI 建議最後）。

### part-007-slice-001: CrowdNarrative schema_version

Status: done — see `.beacon/done/part-007/`

Goal: `CrowdNarrative` 加 `schema_version: str = "1"`（類別字串），供序列化升級判斷。

Candidate scope:
- [ ] `contracts.py`：加欄位 + 契約測試（存在、非數字純量）。
- [ ] CLI JSON 輸出加 `schema_version`。

Verification target:
- Unit: `pytest tests/test_contracts.py -q`
- Regression: `pytest -q` 全綠

Done gate: 欄位存在、非數字、契約與 CLI 同步；`pytest`/`ruff` 綠。

### part-007-slice-002: run --sweep（horizon × intensity 對照表）

Status: done — see `.beacon/done/part-007/`

Goal: `run --sweep` 一次跑 3 horizon × 2 intensity，輸出 6 格對照。

Candidate scope:
- [ ] `cli.py`：`run` 加 `--sweep`；複用 `cmd_run` 產 6 格 JSON array。
- [ ] `tests/test_cli.py`：6 格輸出 + 決定論。

Verification target:
- Unit: `pytest tests/test_cli.py -q`
- Manual QA: `run --sweep --symbol 0056`

Done gate: 6 格正確、決定論、非 sweep 行為不變；`pytest`/`ruff` 綠。

### part-007-slice-003: property-based tests (hypothesis)

Status: done — see `.beacon/done/part-007/`

Goal: dev-dep 加 hypothesis；測決定論 / bucket 單調 / 任意合法 pack 防火牆不變量。

Candidate scope:
- [ ] `pyproject.toml`：`[dev]` 加 `hypothesis`（不進 runtime）。
- [ ] `tests/test_properties.py`：3 個 property 測試（生成器約束合法輸入）。

Verification target:
- Unit: `pytest tests/test_properties.py -q`
- Regression: `pytest -q` 全綠；runtime deps 仍為 []

Done gate: property 測試通過、zero runtime dep 不變；`pytest`/`ruff` 綠。

### part-007-slice-004: PyPI publish-readiness

Status: done — see `.beacon/done/part-007/`

Goal: 驗證可發佈（wheel/sdist、metadata、README render、twine check）。實際上傳為手動。

Candidate scope:
- [ ] `python -m build`；`twine check dist/*`。
- [ ] 檢查 metadata（classifiers、urls、long_description）。
- [ ] 文件記錄發佈步驟（不含 token）。

Verification target:
- Manual QA: `python -m build && twine check dist/*` 全過

Done gate: build + twine check 綠、metadata 完整；發佈步驟文件化。

### part-007-slice-005: rebuild .codegraph index (tooling)

Status: N/A — external tooling, auto-managed (see done snapshot)

Goal: 重建 codegraph 索引（搬移套娃後舊路徑失效）。純工具維護。

Candidate scope:
- [ ] 重建 `.codegraph` 索引指向新單層結構。
- [ ] 抽查查詢命中新路徑。

Verification target:
- Manual QA: codegraph 查詢返回正確新路徑

Done gate: 索引重建、查詢正確。

Dependencies: 各 slice 皆獨立。
