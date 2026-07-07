# part-001 DESIGN

## Goal

讓 `crowd_consensus` 的方向能回應情境語義。新增可選的 `aggregate` 共識模式：由所有
persona 的 stance 多數決聚合出共識，使「深折價+高息」這類明確情境產生方向正確的群眾
傾向。預設維持現行 `hashed` 模式（零回歸）。

## Non-goals

- 不移除或改變 `hashed` 模式行為（它是預設，byte-stable 必須保住）。
- 不引入任何數字純量到 emitted artifact。
- 不改變 persona stance 的計算公式本身（`_stance_for` 的 tilt 邏輯不動）。

## Assumptions

- 現況 `crowd_consensus` 來自 `_internal_view`（`sha256(seed_hash)`）→ 與情境方向無關。
- `_stance_for(persona, consensus, ordinal, pack)` 目前吃 `consensus` 當 baseline lean，
  再疊加 per-axis tilt。個別 persona 已經會回應情境，只有「群眾共識方向」是骰子。
- seed_hash 是既有的決定論來源，可安全用於 tie-break。

## Design Options

- **A. 純聚合**：丟棄 hashed baseline，共識 = 所有 persona stance 的符號多數。
  缺點：破壞既有 hashed 決定論輸出（大量測試/敘事漂移）；破壞性大。
- **B. 模式切換（選定）**：新增 `consensus_mode: Literal["hashed","aggregate"]`，
  預設 `"hashed"`。`aggregate` 走兩階段：先用 hashed consensus 當 baseline 算出所有
  stance，再多數決聚合成最終共識。零回歸 + 新能力並存。
- **C. 加權混合**：hashed 與 aggregate 加權平均。缺點：引入隱性數字調參、難解釋、
  逼近防火牆灰區。捨棄。

## Chosen Design

選 **B（模式切換，兩階段聚合）**。

流程（aggregate 模式）：
1. `base_consensus = _consensus(_internal_view(seed))`（同現況，當 baseline lean）。
2. 對每個 persona 算 `stance = _stance_for(p, base_consensus, ordinal, pack)`。
3. `net = sum(stance)`；`agg = positive if net > T; negative if net < -T; else neutral`
   （T 為小門檻，例如 1，讓明確多數才翻向，避免 1 票就翻）。
4. **tie-break / 邊界決定論**：門檻與比較全用整數，天然決定論；不使用任何依賴
   Python dict/set 迭代序的邏輯。若未來需打破完全平手，用 `int(seed_hash[:2],16)` 決定，
   絕不用內建順序。
5. 回傳 `agg` 當 `crowd_consensus`；persona_samples 的 stance 維持步驟 2 的值。

`hashed` 模式：完全走現況路徑（`crowd_consensus = base_consensus`），不受影響。

參數傳遞：`run_scenario(..., consensus_mode="hashed")` 新增關鍵字參數，預設 `"hashed"`。
CLI 加 `--consensus-mode {hashed,aggregate}`（slice-002 接線）。

## Verification Targets

- Unit：`tests/test_engine.py`（新增 aggregate 測試）+ 既有全套。
- Regression：`hashed` 模式 `narrative_md` + `persona_samples` 與現況 byte-identical。
- 決定論：同 seed 兩次 aggregate → 完全相等。
- 防火牆：`pytest tests/test_contracts.py` 全過；不得新增數字純量欄位。
- `python -O` 契約冒煙仍 enforced。

## Unit Test Strategy

新增（加入 `tests/test_engine.py` 或新檔 `test_consensus_mode.py`）：
- `test_hashed_mode_unchanged`：預設模式輸出與寫死的既有 consensus 相符（回歸鎖）。
- `test_aggregate_consensus_follows_personas`：深折價+高息 seed → aggregate 共識方向
  與多數 persona stance 一致（例如多數 +1 → positive）。
- `test_aggregate_consensus_is_deterministic`：同 seed 跑兩次 aggregate，結果完全相等。
- `test_aggregate_neutral_on_balanced`：正負相抵的情境 → neutral。
- 參數化涵蓋 STOCK_TW 與 PRODUCT_LAUNCH 至少各一情境。

## Manual QA Strategy

CLI 冒煙（需 `$env:PYTHONPATH='src'`）：
- `run --symbol 0056 --scenario 0056_cut`（預設 hashed，輸出應與 baseline 同）。
- slice-002 後：`run --symbol 0056 --scenario 0056_cut --consensus-mode aggregate`
  肉眼確認共識方向與敘事中多數 persona 立場一致。

## Risks

- 「雞生蛋」兩階段若寫成單階段會 baseline 缺失 → stance 全 0 → 恆 neutral。
  緩解：明確用 hashed base_consensus 當步驟 1，測試鎖住非中性情境。
- 門檻 T 設太高 → aggregate 幾乎恆 neutral；太低 → 一票翻向不穩。
  緩解：用代表情境參數化測試校準（深折價+高息應 positive）。
- 破壞 hashed 決定論：緩解＝先寫 `test_hashed_mode_unchanged` 再改 code（TDD）。

## Open Questions

- 門檻 T 的確切值（1 vs 2 vs 依 roster 大小比例）→ 由 slice-001 校準測試決定，先取
  「淨值符號 + 至少 2 票差」的保守設定，再依測試調整。
