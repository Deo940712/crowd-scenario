# part-003 DESIGN

Source: BACKLOG backlog-002 (bug)

## Goal

修正 `swing` horizon 的反應鏈排序等同 `intraday` 的 bug，讓三個 horizon 的
who-moves-first 排序確實各不相同，並用測試鎖住。

## Non-goals

- 不改 stance 計算、consensus、防火牆。
- 不改 intraday / long 的既有排序行為（只讓 swing 成為真正的中間態）。

## Assumptions

- `engine.py`：`_HORIZON_LEAD = {"intraday": 1.0, "swing": 0.0, "long": -1.0}`。
- `_reaction_chain` 用 `movers.sort(key=herding, reverse=bias >= 0)`。
- bug 根因：`bias >= 0` 對 intraday(1.0) 與 swing(0.0) **都為 True** → 兩者同序
  （高 herding 先動）；只有 long(-1.0) 為 False（低 herding 先動）。swing 因此是
  intraday 的別名。
- 現有測試 `test_horizon_changes_reaction_chain_lead` 只比 intraday vs long，沒抓到
  swing 的問題。

## Design Options

- **A. 改門檻為 `bias > 0`**：讓 swing(0.0) 落到 else 分支 = 與 long 同序。只是把
    別名從 intraday 換成 long，沒有給 swing 獨立行為。捨棄。
- **B. swing 用中性排序（選定）**：swing 不做 herding 排序，改用 roster 固定序
    （persona_ids 順序）當「中間態」——不偏快也不偏慢，代表「無明顯領先者」。
    intraday=高 herding 先、long=低 herding 先、swing=roster 序。三者確實不同。
- **C. 為每 horizon 設獨立 key 函式**：最彈性但過度設計，目前只有三個 horizon。捨棄。

## Chosen Design

選 **B**。`_reaction_chain` 的排序改為三分支：
- intraday：`sort(key=herding, reverse=True)`（快跟風者先）
- long：`sort(key=herding, reverse=False)`（慢基本面派先）
- swing：只用 roster 固定序（`order` map），不套 herding

實作上可用一個小 helper 依 `seed.horizon` 選排序策略，或明確 if/elif。保持決定論：
roster 序本就穩定；herding 排序已有 roster 序當 tie-break（L131）。

需同步微調 `_HORIZON_LEAD` 的用法或註解，讓「swing=中性」的語義在程式與 docstring
一致（`_HORIZON_LEAD` 若只被此處用，可考慮改成策略標籤而非數字）。

## Verification Targets

- Unit：`tests/test_engine.py`。
- 三 horizon 排序互不相同（新測試）。
- 決定論：同 seed 同 horizon 兩次結果相同。
- Regression：`pytest -q` 全綠；hashed 敘事對 intraday/long **不得改變**（只有 swing 變）。

## Unit Test Strategy

- `test_swing_order_differs_from_intraday_and_long`：同 seed，三 horizon 的反應鏈第一
    位（`1. ` 後）三者兩兩不同（至少 swing 與 intraday 不同）。
- `test_each_horizon_reaction_chain_is_deterministic`：每 horizon 跑兩次 byte 相同。
- 保留並強化既有 `test_horizon_changes_reaction_chain_lead`。
- 回歸：pin intraday 與 long 的首位 persona（改動前先量測寫死），確保只有 swing 變。

## Manual QA Strategy

`run --symbol 0056 --scenario evt --horizon {intraday,swing,long}` 三次，肉眼確認
反應鏈領先者不同。

## Risks

- swing 改動可能讓某些既有 swing 敘事漂移 → 這是預期的（修 bug），但要確認 intraday/
    long 零漂移。緩解：回歸測試 pin intraday/long 首位。
- `_HORIZON_LEAD` 若他處也用到 → 先 grep 確認只在 `_reaction_chain` 使用再動。

## Open Questions

- swing 用 roster 序是否為最自然的「中間態」語義？替代：herding 中位數附近優先。
    先採 roster 序（最簡單、最決定論），QA 不滿意再議。
