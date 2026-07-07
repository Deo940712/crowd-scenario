# part-004 TODO

Design authority: `.beacon/parts/part-004/DESIGN.md`
Source: BACKLOG backlog-001

## SLICE Map

### part-004-slice-000: DECIDE storylines — implement or delete (design-only)

Status: done — DECIDED B (implement counterfactual storylines). See DESIGN Open Questions.

Goal:
定案 `storylines` 要「實作反事實敘事（B）」還是「刪除欄位（A）」。

Outcome:
選定 B（實作反事實敘事）。slice-001 scope 收斂為 B。

### part-004-slice-001: Apply the storylines decision

Status: done — archived at `.beacon/done/part-004/part-004-slice-001-done-current.md`

Goal (B):
`compose_divergence` 依 divergence_bucket + 方向組合產生條件式、無數字的 storylines。

Candidate scope (B):
- [x] `composer.py`：`_storylines_for(crowd, external, bucket)` 查表產生 storylines。
- [x] `compose_divergence` 填 `storylines`。
- [x] `tests/test_composer.py`：high/low gap storylines、決定論、無數字 token。

Forbidden scope:
- 數字純量進 storylines。
- 讓引擎知道 external_posture。

Verification target:
- Unit: `pytest tests/test_composer.py -q`（全過）
- Regression: `pytest -q` 全綠（95）
- 防火牆: storylines 過 `scan_violations`
- Manual QA: 印 HIGH-gap storylines 肉眼確認

Done gate:
- 反事實 storylines 落實、防火牆不變量保持、`pytest`/`ruff` 綠。 ✓

Dependencies: slice-001 依賴 slice-000 定案（已定 B）。
