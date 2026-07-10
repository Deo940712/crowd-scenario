# DONE — part-010: Case studies (3 slices)

Source: 內部評估「從 feature building 轉向 evidence building」+ Codex review（真實
case study 讓它從技術原型變成有說服力的作品）。

## slice-001: runner + CASE A — DONE

- `case_studies/runner.py`：共用 runner（輸入 → buckets → 三模式 → sweep → divergence）。
- `case_studies/cases.py`：三案例 CaseSpec；`case_studies/__init__.py`（package marker，
  不進 wheel）；`case_studies/report.py`（`report.py A|B|C` 重現輸出）。
- `case_studies/case_a_etf_discount.md`：8 段誠實模板（含「哪裡不能信」），**實測值**。
- `tests/test_case_studies.py`：可重現 / 結論與文件 front-matter 一致 / limitations 段
  存在 / 無 raw 洩漏。`pyproject.toml` pytest pythonpath 加 repo root。

## slice-002: CASE B + CASE C — DONE

- `case_studies/case_b_price_hike.md`（product_launch；8 cohort 全反對；HIGH divergence）。
- `case_studies/case_c_premium_chase.md`（stock_tw 溢價追高；HIGH divergence）。
- 測試自動涵蓋三案例（12 case tests）。

## slice-003: README 導流 — DONE

- `case_studies/README.md`：索引頁（三案例表 + 重現指令）。
- `README.md` + `README.zh-TW.md`：Case studies 章節（三連結 + 一句話）。

## Key evidence produced

| case | domain | default (aggregate_neutral) | hashed | 看點 |
| --- | --- | --- | --- | --- |
| A ETF 深折價高息 | stock_tw | positive | positive | 三模式收斂（明確情境）|
| B 漲價低價值 | product_launch | negative | **neutral** | default 修正 hashed 骰子 |
| C 溢價追高 | stock_tw | negative | **neutral** | 群眾潑冷水 FOMO |

CASE B/C 是 0.2.0 default 遷移的活教材：hashed 對明確負向情境擲出 neutral，
aggregate_neutral 正確給 negative。

## Verification evidence

- `pytest -q` → **244 passed**（含 12 case tests）
- `ruff check .` → clean
- 三案例：可離線重現、結論與文件一致、含限制段、無 raw 數字洩漏
- CJK：三案例文件 + 兩份 README + 索引 → 無 mojibake
- `report.py A|B|C` 可重現；`case_studies/` 不進 wheel

## Non-goals honored

- 無回測/準確率宣稱；全程條件式語氣；未為好看調參（實測值直接使用）。

## Incidents

None. (slice-001 golden 全用實測值捕捉，非虛構。)
