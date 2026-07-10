# part-013 TODO

Design authority: `.beacon/parts/part-013/DESIGN.md`

**GATED**: 本 PART 的任何 slice 在 part-008 完成並產出明確推薦前，不得 promote。

## SLICE Map

### part-013-slice-001: Gate check + migration impact survey (design-only)

Status: done — gate satisfied; execute (not no-op). See `.beacon/done/part-013/migration-impact.md`

Goal:
確認 gate 三條件滿足；全面盤點 default 變更的影響面（所有未指定 mode 的呼叫點、
測試斷言、case studies、報告、文件）。

Candidate scope:
- [ ] 核對 part-008 `consensus-evaluation.md` 推薦與五準則對照。
- [ ] grep 全 repo 未指定 `consensus_mode` 的呼叫點清單，分類
      「default 行為測試 / 模式語義測試 / 文件範例」。
- [ ] 產出遷移清單（或 no-change 決策草稿）。

Forbidden scope:
- 改任何 code。

Verification target:
- 影響面清單完整（清單項目與 grep 結果數一致）。

Done gate:
- 明確結論：執行遷移（附清單）或 no-op 收檔（附決策文件）。

### part-013-slice-002: Execute default migration (conditional)

Status: done — migrated to aggregate_neutral (0.2.0). See `.beacon/done/part-013/`

Goal:
依 slice-001 清單執行 default 變更：engine + CLI + 測試遷移 + 文件 + 版本 bump。

Candidate scope:
- [ ] `engine.py` / `cli.py` default 變更。
- [ ] 測試遷移（default 行為類更新期望；hashed 語義類顯式標注）。
- [ ] `test_default_mode_is_<selected>` 新增。
- [ ] README（英+中）/ CHANGELOG / help 文字同步；版本 0.2.0。
- [ ] （若存在）case studies / 報告輸出再生。

Forbidden scope:
- 移除任何模式。
- 未列入 slice-001 清單的順手改動。

Verification target:
- Unit + Regression: `pytest -q` 全綠、`ruff` clean、`python -O` 契約
- Manual QA: CLI default 冒煙 + README 範例抽跑

Done gate:
- 新 default 生效、hashed golden 保留、文件與行為一致、版本已 bump。

Dependencies: slice-002 依賴 slice-001 的「執行遷移」結論；若結論為 no-op，
本 slice 標記 cancelled 並歸檔決策文件。
