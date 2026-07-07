# DONE — part-006 / slice-002: Intensity-scaled chain length

Source: BACKLOG backlog-003 (secondary slice).

## Goal (achieved)

severe intensity 時反應鏈展開更多步；mild 維持現況（零漂移）。

## What shipped

- `engine.py::_reaction_chain`：severe 且 movers>2 且第三個 mover 不等於 tail 時，
  在 tail 前插入一個額外中間步（「也被帶動」）。mild 完全走原 3 步路徑。
  防禦：`movers[2] is not tail` 避免 3-mover/0-anchor 邊界重複 persona。
- `tests/test_engine.py`：+3（severe>mild 步數、mild pin=3 回歸、severe 決定論）。

## Verification evidence

- `pytest -q` → **110 passed**（107 + 3）
- `ruff check .` → clean
- Manual QA: mild=3 步、severe=4 步；severe 鏈無重複 persona。

## Incidents

None.
