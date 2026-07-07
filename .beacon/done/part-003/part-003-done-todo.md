# part-003 TODO

Design authority: `.beacon/parts/part-003/DESIGN.md`
Source: BACKLOG backlog-002

## SLICE Map

### part-003-slice-001: Give swing a distinct middle-ground ordering

Status: done — archived at `.beacon/done/part-003/part-003-slice-001-done-current.md`

Goal:
`_reaction_chain` 讓 swing 用 roster 固定序（中間態），與 intraday（高 herding 先）、
long（低 herding 先）三者排序確實不同，決定論不變。

Outcome:
同 seed 三 horizon 的反應鏈領先者不同；intraday/long 敘事零漂移，只有 swing 改變。

Candidate scope:
- [ ] grep 確認 `_HORIZON_LEAD` 僅在 `_reaction_chain` 使用。
- [ ] `engine.py`：反應鏈排序改三分支（intraday/long 用 herding 方向、swing 用 roster 序）。
- [ ] 同步 docstring / `_HORIZON_LEAD` 語義註解。
- [ ] `tests/`：先 pin intraday+long 首位（回歸鎖），再加 swing-differs + 三 horizon 決定論測試。

Forbidden scope:
- stance / consensus / 防火牆邏輯。
- 改變 intraday 或 long 的既有排序。

Verification target:
- Unit: `pytest tests/test_engine.py -q`
- Regression: `pytest -q` 全綠；intraday/long 首位 pin 不變
- Manual QA: `run ... --horizon {intraday,swing,long}` 三者領先者不同

Done gate:
- 三 horizon 排序互異、swing 有獨立中間態行為、intraday/long 零漂移、決定論保持；
  `pytest`/`ruff` 綠。

Dependencies: 無。
