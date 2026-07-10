# part-010 TODO

Design authority: `.beacon/parts/part-010/DESIGN.md`

## SLICE Map

### part-010-slice-001: Case study runner + CASE A (ETF 深折價高息)

Status: done — see `.beacon/done/part-010/`

Goal:
建 `case_studies/` 基礎架構（共用 runner、可重現性測試）+ 第一份完整 case study。

Candidate scope:
- [ ] `case_studies/runner.py`：共用執行邏輯（輸入 → buckets → 兩模式 → sweep → divergence）。
- [ ] `case_studies/case_a_etf_discount.md`：完整 8 段模板（含「哪裡不能信」）。
- [ ] `case_studies/run_case_a.py` 或 runner 參數化。
- [ ] `tests/test_case_studies.py`：可重現性 + 結論一致 + limitations 段存在。

Forbidden scope:
- 調引擎參數讓結果「好看」。
- 預測性用詞。

Verification target:
- Unit: `pytest tests/test_case_studies.py -q`
- Regression: `pytest -q` 全綠
- Manual QA: 人工閱讀 CASE A 全文

Done gate:
- CASE A 可重現、結論與文件一致、誠實段落齊全。

### part-010-slice-002: CASE B (產品漲價) + CASE C (溢價追高)

Status: done — see `.beacon/done/part-010/`

Goal:
用 slice-001 的架構補完另外兩份 case study。

Candidate scope:
- [ ] `case_studies/case_b_price_hike.md`（PRODUCT_LAUNCH；divergence 對照 PM 假想判讀）。
- [ ] `case_studies/case_c_premium_chase.md`（STOCK_TW 反向情境；severe 鏈條 + variants）。
- [ ] 測試擴充涵蓋三個 case。

Forbidden scope:
- 同 slice-001。

Verification target:
- Unit: 三 case 測試全綠
- Manual QA: 人工閱讀 B/C 全文

Done gate:
- 三份 case study 齊全、全部可重現、誠實模板一致。

Dependencies: slice-002 依賴 slice-001。

### part-010-slice-003: README 導流 + case study 索引

Status: done — see `.beacon/done/part-010/`

Goal:
讓看 repo 的人第一眼找到證據：README（英+中）加 case studies 章節與索引。

Candidate scope:
- [ ] README.md / README.zh-TW.md 加「Case studies」段（一句話 + 三連結）。
- [ ] `case_studies/README.md` 索引頁（列三案例 + 執行方式）。

Verification target:
- Manual QA: 連結有效、描述與內容一致。

Done gate:
- 從 repo 首頁兩次點擊內可達任一 case study。

Dependencies: slice-003 依賴 slice-002。
