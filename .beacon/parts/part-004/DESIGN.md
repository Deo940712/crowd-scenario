# part-004 DESIGN

Source: BACKLOG backlog-001 (design-debt)

## Goal

解決 `NarrativeDivergence.storylines` 死欄位：目前 `compose_divergence` 從不填它，
永遠是空 tuple。決定「實作」或「刪除」，讓契約不再有半成品欄位。

## Non-goals

- 不引入任何數字純量（storylines 只能是類別性敘事字串）。
- 不讓引擎知道 external_posture（divergence 是 report-time，防火牆外）。

## Assumptions

- `contracts.py`：`NarrativeDivergence.storylines: tuple[str, ...] = ()`。
- `composer.py::compose_divergence` 計算 `gap = |crowd - external|`（0|1|2）→ bucket +
    intensity，但沒填 storylines。
- storylines 是純敘事（字串 tuple），不違反防火牆。

## Design Options

- **A. 刪除欄位**：最小、最誠實。若無明確用途就移除，契約更乾淨。但失去一個契合
    「排練」定位的表達位（反事實敘事）。需同步移除相關測試/文件引用。
- **B. 實作反事實敘事（選定，待你定案）**：在 `compose_divergence` 依 divergence_bucket
    產生 1-3 條類別性 storyline，例如：
    - LOW：「群眾與你的判讀一致，無明顯分歧劇本。」
    - MEDIUM：「若群眾對而你的判讀偏移，這類情境可能…（條件式）。」
    - HIGH：「群眾與你顯著分歧：若群眾對，你可能低估X；若你對，群眾正在追逐雜訊。」
    全條件式、無數字、非建議。與 crowd_consensus vs external_posture 的方向組合對應。

## Chosen Design

**待你定案 A 或 B**（這是 design-only 決策點）。傾向 **B**：反事實 storyline 契合
「排練而非預測」的定位，且是純類別敘事、零防火牆風險。若你選 A（刪除），slice 改為
移除欄位 + 清理引用。

若 B：
- `composer.py` 加 `_storylines_for(crowd, external, bucket) -> tuple[str, ...]`
    （查表，決定論，條件式語氣，無數字）。
- `compose_divergence` 填 `storylines=...`。
- 方向組合（crowd × external × bucket）對應不同 storyline 模板。

## Verification Targets

- Unit：`tests/test_contracts.py` 或新 `tests/test_composer.py`。
- storylines 非空（B）或欄位移除（A）。
- 防火牆：storylines 內不得含數字市場 token（沿用 scanner 精神斷言）。
- 決定論：同輸入同 storylines。

## Unit Test Strategy

若 B：
- `test_divergence_high_gap_has_storylines`：HIGH divergence → storylines 非空。
- `test_divergence_low_gap_storyline_is_agreement`：LOW → 一致性劇本。
- `test_storylines_are_deterministic`：同輸入 byte 相同。
- `test_storylines_carry_no_numeric_token`：`scan_violations` 對每條 storyline 為空。
若 A：
- 移除 storylines 相關斷言；加 `test_divergence_has_no_storylines_field`。

## Manual QA Strategy

Python：`compose_divergence(narrative, posture_from_score(0.9))`（製造 HIGH gap），
印 `.storylines` 肉眼確認（B）或確認欄位不存在（A）。

## Risks

- B 的 storyline 模板可能寫成「預測」語氣 → 嚴格條件式 + 過 scanner。
- A 刪欄位是破壞性 API 變更（但 0.1.0 未發佈，可接受）。

## Open Questions

- **A 還是 B？** → **DECIDED: B（實作反事實敘事）**。理由：契合 rehearsal 定位、
  純類別字串零防火牆風險、比刪欄位更有價值。slice-001 scope 收斂為 B。
