# part-005 TODO

Design authority: `.beacon/parts/part-005/DESIGN.md`
Source: BACKLOG backlog-004

## SLICE Map

### part-005-slice-001: Real-data worked example + docs

Status: done — archived at `.beacon/done/part-005/part-005-slice-001-done-current.md`

Goal:
加 `examples/real_data.py`（注入式資料源，自帶離線 fake fetch）+ README「Feeding real
data」章節 + 測試，證明真實分數餵入後防火牆仍成立。

Outcome:
使用者有一個可跑、可仿的範例，示範安全接真實輿情/市場分數；原始數字不外洩。

Candidate scope:
- [ ] `examples/real_data.py`：fake `fetch_metrics` → make_seed → run_scenario，印
      categorical 結果 + 註解防火牆邊界。
- [ ] README 加「Feeding real data」章節，連到範例。
- [ ] `tests/test_examples.py`：runs-categorical / no-raw-leak / deterministic。
- [ ] 確認 `examples/` 的 lint（ruff）與是否進 wheel（傾向不進）。

Forbidden scope:
- 真實網路 / 外部依賴。
- 改引擎 / 契約 / 防火牆邏輯。

Verification target:
- Unit: `pytest tests/test_examples.py -q`
- Regression: `pytest -q` 全綠
- `ruff check .`
- Manual QA: `python examples/real_data.py`

Done gate:
- 範例可跑、輸出 categorical、原始分數不外洩、決定論；文件連結正確；`pytest`/`ruff` 綠。

Dependencies: 無。
