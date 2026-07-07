# DONE — part-004 / slice-001: Implement counterfactual storylines

Source: BACKLOG backlog-001. Decision (slice-000): B (implement, not delete).

## Goal (achieved)

`compose_divergence` 依 divergence_bucket + 方向組合產生條件式、無數字的 storylines，
`NarrativeDivergence.storylines` 不再是死欄位。

## What shipped

- `composer.py`：
  - `_CROWD_LEAN` / `_YOUR_LEAN` 類別性 lean 措辭表。
  - `_storylines_for(crowd, external, bucket)`：純函式，依 LOW/MEDIUM/HIGH 產生 2-4 條
    條件式反事實 storyline（全「若…可能…」語氣、無數字、非建議）。
  - `compose_divergence` 填 `storylines`。
- `tests/test_composer.py`（新檔）：5 個測試。

## Firewall / determinism

- storylines 全為類別字串、無數字純量；每條過 `scan_violations`（測試鎖）。
- 純函式，同輸入同輸出（決定論測試鎖）。
- 未讓引擎知道 external_posture（divergence 仍是 report-time）。

## Verification evidence

- `pytest -q` → **95 passed**（90 + 5）
- `ruff check .` → clean
- Manual QA: HIGH divergence 產出 4 條反事實劇本，全條件式、無數字。

New tests:
- `test_high_divergence_has_storylines`
- `test_low_divergence_storyline_signals_agreement`
- `test_storylines_are_deterministic`
- `test_storylines_carry_no_numeric_market_token`
- `test_storylines_reachable_via_posture_from_score`

## Incidents

None.
