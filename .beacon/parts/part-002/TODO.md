# part-002 TODO

Design authority: `.beacon/parts/part-002/DESIGN.md`

## SLICE Map

### part-002-slice-001: CLI --metrics with fail-fast + fallback warning

Status: done — archived at `.beacon/done/part-002/part-002-slice-001-done-current.md`

Goal:
`run` 加 `--metrics '<json>'` 自訂輸入；優先序 override > fixture > fallback；
fallback 印 stderr 警告；壞 JSON / 缺 metric → 乾淨錯誤 + 非零退出。

Outcome:
`run --symbol X --scenario Y --metrics '{...}'` 用使用者輸入跑；無 fixture 無 metrics
印 warning 仍跑；錯誤輸入不吐 traceback。原始數字不外洩。

Candidate scope:
- [ ] `cli.py`：`run` 加 `--metrics`（字串，預設 None）。
- [ ] `cli.py`：`_metrics_for(domain, symbol, override=None)` 新簽名；fallback 印 stderr
      warning。
- [ ] `cli.py`：`cmd_run` parse `--metrics`（`json.loads`）；JSON 壞 / 缺 metric
      (`ContractError`) → 印 error 到 stderr、`return 2`。
- [ ] `tests/test_cli.py`：6 個新測試（accepts / override-beats-fixture / invalid-json /
      missing-metric / fallback-warns / no-raw-leak）。
- [ ] `cli.py` docstring + README CLI 範例加 `--metrics`。

Forbidden scope:
- 引擎 / 契約 / 防火牆邏輯。
- `verify --metrics`（本 part non-goal）。
- 回顯原始數字到 JSON 輸出。

Verification target:
- Unit: `pytest tests/test_cli.py -q`（新測試全過）
- Regression: `pytest -q` 全綠
- `ruff check .`
- Manual QA: 三條 CLI 冒煙（有效 metrics / 無 fixture warning / 壞 JSON 乾淨錯誤）

Done gate:
- `--metrics` 可用、優先序正確、fallback 印警告、錯誤乾淨（無 traceback）、
  原始數字不外洩；`pytest`/`ruff` 綠。

Dependencies: 無（獨立於 part-001）。
