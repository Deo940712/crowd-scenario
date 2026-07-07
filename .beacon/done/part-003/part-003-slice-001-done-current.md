# DONE — part-003 / slice-001: Give swing a distinct middle-ground ordering

Completed snapshot of the promoted CURRENT for this slice.
Source: BACKLOG backlog-002 (bug).

## Goal (achieved)

修正 `swing` horizon 反應鏈排序等同 `intraday` 的 bug，讓三個 horizon 排序確實不同。

## Root cause

`_HORIZON_LEAD = {intraday:1.0, swing:0.0, long:-1.0}` + `reverse=bias >= 0`：
`bias >= 0` 對 intraday(1.0) 與 swing(0.0) **都為 True** → 兩者同以 herding 降序排序
（快跟風者先動）。swing 因此是 intraday 的別名，只有 long 不同。

## What shipped

- `engine.py`：
  - `_HORIZON_LEAD`（數字 bias 表）→ `_HORIZON_ORDER`（語義策略表）：
    `{intraday: "herding_desc", swing: "roster", long: "herding_asc"}`。
  - `_reaction_chain` 排序改三分支：intraday 依 herding 降序、long 升序、
    **swing 保留 roster 序**（不套 herding），成為真正的中間態。
  - docstring 更新。
- `tests/test_engine.py`：新增 6 個測試（_chain_lead helper + 5 個測試）。

## Result (before → after, seed 0056/evt)

| horizon | before (lead) | after (lead) |
| --- | --- | --- |
| intraday | PTT/Dcard 風向 | PTT/Dcard 風向 (unchanged) |
| swing | **PTT/Dcard 風向 (= intraday!)** | **存股族 (roster-first mover)** |
| long | 外資視角 | 外資視角 (unchanged) |

三 horizon 領先者現在確實互異；intraday/long 零漂移。

## Verification evidence

- `pytest -q` → **90 passed**（84 + 6）
- `ruff check .` → All checks passed
- Manual QA: `run --horizon {intraday,swing,long}` → 三者領先者不同（PTT/存股族/外資）

New tests:
- `test_all_three_horizons_lead_with_distinct_personas`
- `test_intraday_and_long_leads_are_pinned`（回歸鎖：intraday/long 零漂移）
- `test_swing_lead_is_roster_first_mover`
- `test_each_horizon_reaction_chain_is_deterministic`（參數化 × 3）

## Firewall / determinism

- 未動 stance / consensus / 防火牆。
- 決定論保持：roster 序穩定；herding 排序仍以 roster 序為基底（tie-break 一致）。

## Incidents

None.
