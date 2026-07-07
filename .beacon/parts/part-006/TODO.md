# part-006 TODO

Design authority: `.beacon/parts/part-006/DESIGN.md`
Source: BACKLOG backlog-003

## SLICE Map

### part-006-slice-001: Optional voice variants (deterministic pick)

Status: done — archived at `.beacon/done/part-006/part-006-slice-001-done-current.md`

Goal:
新增選配 `voice_variants` 表 + engine `_pick_voice`（seed_hash 決定選句），有 variants
的 persona 敘事可多樣、同 seed 決定論；無 variants 的 pack 零漂移。

Outcome:
不同 seed 對有 variants 的 persona 可得不同敘事；既有無 variants 行為 byte-identical。

Candidate scope:
- [ ] `domains/base.py`：`DomainPack` 加 `voice_variants`（預設空）；`validate_pack` 驗證。
- [ ] `engine.py`：`_pick_voice(pack, persona, stance, seed_hash)`；`_excerpt_for` +
      `_reaction_chain._line` 改用它。
- [ ] `domains/stock_tw.py`：為幾個代表 persona 加 2-3 句變體（示範）。
- [ ] `tests/`：決定論 / 跨 seed 多樣 / no-variants 回歸 / 防火牆 / validate_pack 壞值。

Forbidden scope:
- stance / consensus / 防火牆邏輯核心。
- 隨機（非 seed_hash）選句。
- 改變無 variants pack 的既有輸出。

Verification target:
- Unit: `pytest tests/test_engine.py tests/test_contracts.py -q`
- Regression: `pytest -q` 全綠；no-variants 敘事 byte-stable
- Manual QA: `run --seed 1` vs `--seed 2` 敘事可不同、同 seed 相同

Done gate:
- variants 決定論 + 跨 seed 多樣、無 variants 零漂移、防火牆保持；`pytest`/`ruff` 綠。

### part-006-slice-002: (optional) intensity-scaled chain length

Status: done — archived at `.beacon/done/part-006/part-006-slice-002-done-current.md`

Goal:
severe intensity 時反應鏈展開更多步；mild 維持現況。

Candidate scope:
- [ ] `engine.py`：`_reaction_chain` 依 intensity 調整步數。
- [ ] `tests/`：severe vs mild 步數不同、決定論、mild 回歸。

Forbidden scope:
- 改變 mild 的既有輸出。

Verification target:
- Unit + Regression: `pytest -q` 全綠；mild byte-stable

Done gate:
- severe 展開、mild 零漂移、決定論；`pytest`/`ruff` 綠。

Dependencies: slice-002 獨立於 slice-001，但建議 slice-001 先。
