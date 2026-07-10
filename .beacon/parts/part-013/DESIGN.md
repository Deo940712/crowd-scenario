# part-013 DESIGN

Source: 原 part-008（直接改 aggregate default）的替代——改為**證據閘門版**：
只有在 part-008 的評估矩陣給出明確推薦後，才執行 default 變更。

## Goal

根據 `part-008` 產出的 `consensus-evaluation.md` 決策，執行（或明確不執行）
public default `consensus_mode` 的遷移。這是一個 **gated PART**：前置條件不滿足
就不得 promote。

## Non-goals

- 不在 part-008 完成前做任何 default 變更。
- 不移除任何既有模式（hashed / current aggregate 永遠保留為顯式選項）。
- 不做「為了改而改」——若 part-008 結論是「維持現況」，本 PART 以 no-op 收檔，
  只留決策記錄。

## Gate（promote 前置條件，缺一不可）

1. part-008 全部 slices 完成並歸檔。
2. `consensus-evaluation.md` 明確推薦一個 default（或明確建議維持現況）。
3. 推薦附有五項準則（可解釋性/語義一致性/中性穩定性/決定論/無 case-specific hack）
   的逐條對照。

## Assumptions

- 若推薦變更，最可能的候選是 neutral-baseline aggregate 或 current aggregate。
- default 變更是公開 API 行為變更：不指定 mode 的所有呼叫者輸出都會漂移。
- 版本語義：0.x 階段允許行為變更，但需在 CHANGELOG/README 顯著標注。

## Design（若 gate 通過且推薦變更）

1. `engine.py`：`run_scenario(..., consensus_mode=<新 default>)`。
2. `cli.py`：`--consensus-mode` default 同步。
3. 測試遷移策略（承襲原 part-008 草案的功課）：
   - 先 grep 所有未指定 mode 的 `run_scenario(` 呼叫點與斷言。
   - 「測的是 default 行為」→ 更新期望值為新 default。
   - 「測的是 hashed 語義」→ 顯式加 `consensus_mode="hashed"`（golden 保留）。
   - 新增 `test_default_mode_is_<selected>`。
4. 文件：README（英+中）default 說明、`--consensus-mode` help、HANDOFF 若仍引用舊
   default 一併更新；CHANGELOG 記錄行為變更。
5. 版本號 bump（0.1.0 → 0.2.0，行為變更級）。

## Design（若 gate 通過但推薦維持現況）

- 不改 code。寫 `.beacon/done/part-013/decision-no-change.md`：引用 part-008 證據、
  說明為何維持、標注未來重新評估的觸發條件（例如新增 domain 後語義分布改變）。

## Verification Targets

- 變更路徑：`pytest -q` 全綠（含遷移後 golden）、`ruff` clean、`python -O` 契約、
  CLI 冒煙（default 與顯式模式各一）。
- 不變路徑：決策文件完整、PLAN 標記 no-op 完成。

## Unit Test Strategy

（變更路徑）
- `test_default_mode_is_<selected>`：不指定 == 顯式 selected。
- `test_hashed_explicit_golden_unchanged`：顯式 hashed 與 part-001 pin 一致。
- `test_current_aggregate_explicit_unchanged`（若 selected 是 neutral 版）。
- CLI：JSON `consensus_mode` 反映新 default。

## Manual QA Strategy

- `run`（不指定 mode）→ JSON default 正確。
- README 範例輸出說明與實際行為一致（抽跑一個範例）。

## Risks

- golden 漂移面大（test_engine/test_cli/test_narrator/case_studies/report 都可能有
  隱含 default 斷言）→ 遷移前全面 grep，分「default 行為測試」與「模式語義測試」兩類處理。
- part-010/011 若先完成，case studies 與報告內的 default 輸出也要同步再生。
- 文件與行為不同步 → done gate 包含文件抽查。

## Open Questions

- 無（本 PART 的所有開放問題都由 part-008 的證據回答）。
