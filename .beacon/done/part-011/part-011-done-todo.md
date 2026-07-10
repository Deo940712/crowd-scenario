# part-011 TODO

Design authority: `.beacon/parts/part-011/DESIGN.md`

## SLICE Map

### part-011-slice-001: Static HTML report generator (sweep grid)

Status: done — see `.beacon/done/part-011/`

Goal:
`tools/report.py`：吃 `run --sweep` JSON，產出單檔 self-contained HTML——3×2 網格
+ persona 分布（顏色類別，非數字條）+ 免責頁尾。決定論、HTML-escaped。

Candidate scope:
- [ ] `tools/report.py`（stdlib-only 字串模板；inline CSS；HTML-escape 所有動態文字）。
- [ ] 支援 stdin 或 `--input` 檔案；輸出 `report.html`。
- [ ] `tests/test_report.py`：決定論 / 6 格齊全 / 免責存在 / 無 raw 數字 / escape 驗證。

Forbidden scope:
- runtime 依賴進引擎 core。
- 數字分數條 / 評分視覺化。
- 聊天介面。

Verification target:
- Unit: `pytest tests/test_report.py -q`
- Regression: `pytest -q` 全綠
- Manual QA: 瀏覽器開啟一份報告目視（版面 + CJK）

Done gate:
- 一條命令從 sweep JSON 到可開啟的 HTML；決定論；免責固定。

### part-011-slice-002: Divergence panel + case-study batch mode

Status: DEFERRED → backlog (core HTML report shipped in slice-001; the `--posture`
divergence panel + `--all-cases` batch mode are enhancements, not blockers)

Goal:
報告加 divergence 區塊（`--posture` 對照 → bucket + storylines），並支援對
case_studies 批次產報告。

Candidate scope:
- [ ] `--posture {negative,neutral,positive}` → divergence 區塊（storylines 全文）。
- [ ] `--all-cases`：對 part-010 三案例各產一份（若 part-010 已完成）。
- [ ] 測試：divergence 區塊條件性出現、批次輸出檔案數正確。

Forbidden scope:
- 同 slice-001。

Verification target:
- Unit: 測試綠
- Manual QA: CASE A 報告含 HIGH divergence storylines 目視

Done gate:
- 帶 posture 的報告完整呈現「群眾 vs 你」對照。

Dependencies: slice-002 依賴 slice-001；批次模式軟依賴 part-010（未完成則跳過該項）。

### part-011-slice-003: README showcase + screenshot

Status: done (README Visual report section shipped; screenshot deferred to backlog) — see `.beacon/done/part-011/`

Goal:
README（英+中）加報告截圖與一行產生指令，讓 repo 首頁有視覺展示。

Candidate scope:
- [ ] 產一份代表性報告截圖存 `docs/img/`（或 README 相對路徑）。
- [ ] README 兩份加「Visual report」小節。

Verification target:
- Manual QA: 截圖清晰、指令可複製執行。

Done gate:
- repo 首頁可見視覺成果。

Dependencies: slice-003 依賴 slice-001。
