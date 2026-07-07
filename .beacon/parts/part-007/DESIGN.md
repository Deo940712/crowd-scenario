# part-007 DESIGN

Source: BACKLOG backlog-005 (idea, 拆成多個獨立小 slice)

## Goal

一組獨立的雜項增強，彼此無強依賴，各自可獨立 promote：
schema_version、`run --sweep`、property-based 測試、PyPI 發佈、重建 codegraph 索引。

## Non-goals

- 不改引擎核心邏輯 / 防火牆語義（多為周邊 / 工具 / 打包）。
- 不引入 runtime 依賴（hypothesis 只進 dev deps）。

## Assumptions

- 專案已綠燈（84 tests, ruff clean），git 已上 GitHub main。
- `CrowdNarrative` 是 frozen dataclass；加欄位需同步契約測試。
- pyproject 已備 build/wheel 設定（py.typed 已驗證進 wheel）。

## Design Options / Chosen (per sub-item)

- **schema_version**：`CrowdNarrative` 加 `schema_version: str = "1"`（類別字串，非數字
    純量 → 不違反防火牆）。序列化存檔後有升級判斷依據。低風險。
- **run --sweep**：CLI `run` 加 `--sweep`，一次跑 3 horizon × 2 intensity（6 格）輸出
    對照表（JSON array 或表格）。純 CLI 層，複用 `cmd_run` 邏輯。
- **property-based 測試**：dev-dep 加 `hypothesis`；測決定論、bucket 單調性、任意合法
    pack 的防火牆不變量。只進 `[dev]`，不影響 runtime zero-dep。
- **PyPI 發佈**：驗證 wheel/sdist、metadata、README render；`twine check`；（實際上傳需
    帳號/token，屬手動步驟，slice 只到「可發佈就緒」）。
- **codegraph 重建**：純工具維護（搬移套娃後舊索引路徑失效），非產品碼。

## Verification Targets（per slice）

- schema_version：契約測試 + 欄位存在 + 非數字。
- sweep：CLI 測試（6 格輸出、決定論）。
- property tests：hypothesis 案例通過、CI 綠。
- PyPI：`python -m build` + `twine check` 通過。
- codegraph：索引重建成功、查詢命中新路徑。

## Unit Test Strategy

- `test_crowd_narrative_has_schema_version` + 契約非數字斷言。
- `test_cli_sweep_outputs_all_horizon_intensity`（6 格）+ 決定論。
- hypothesis：`test_determinism_property`、`test_bucket_monotonic_property`、
    `test_any_pack_firewall_property`。

## Manual QA Strategy

- `run --sweep --symbol 0056`：肉眼確認 6 格對照。
- `python -m build && twine check dist/*`。

## Risks

- schema_version 加欄位影響 `test_crowd_narrative_has_no_numeric_modifier_field` 類斷言
    → 確認字串欄位不誤判。
- hypothesis 若生成非法 pack 需正確被 validate_pack 擋（測試策略要約束生成器）。

## Open Questions

- 這些 sub-item 各自成 slice（可獨立 promote），優先序由你決定。PyPI 發佈通常最後。
