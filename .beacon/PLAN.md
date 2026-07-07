# Beacon Plan

## Project Goal

crowd-scenario：deterministic、firewalled、domain-pluggable 的群眾情境**排練**器
（rehearsal，非 forecast）。讀 bucketed `ScenarioSeed`，只吐 categorical
`crowd_consensus ∈ {negative,neutral,positive}` + 敘事，任何數字純量都不得離開引擎。
本階段目標：把「群眾傾向」從純骰子升級為能回應情境語義，並讓 CLI 可實際使用。

## Non-goals

- 不做真實預測/回測（定位是排練，不是 forecast）。
- 不新增任何 runtime 依賴（`dependencies = []` 是刻意的，維持 stdlib-only）。
- 不引入任何數字純量到 emitted artifact（防火牆紅線）。
- 不改變 `hashed` 模式的既有決定論輸出（byte-stable 回歸鎖住）。

## PARTs

| PART | Status | Goal | Design | TODO |
| --- | --- | --- | --- | --- |
| part-001 | done (slices 001+002) | 共識可回應情境語義（aggregate 模式）+ CLI 接線 | `.beacon/parts/part-001/DESIGN.md` | `.beacon/done/part-001/` |
| part-002 | planned | CLI 可輸入自訂 metrics（`--metrics`） | TBD | TBD |

## Success Criteria

- `aggregate` 共識模式：明確情境（深折價+高息）→ 共識方向與多數 persona stance 一致。
- `hashed` 模式輸出與現況 byte-identical（零回歸）。
- CLI 可用 `--metrics` 餵真實輸入，缺值時 fail-fast 或明確警告（不靜默吞錯）。
- 全程維持：`pytest` 全綠、`ruff` clean、`python -O` 契約 enforced、防火牆不變量不破。

## Global Risks

- 共識聚合的「雞生蛋」：`_stance_for` 需要 baseline consensus，aggregate 需兩階段
  且必須維持決定論（tie-break 用 seed hash，不用 Python 內建順序）。
- 動引擎易破壞 `hashed` 決定論 → 必須先寫回歸鎖再改。
- 掃描器/敘事改動易誤殺乾淨 deterministic prose（加碼/停損是合法語音）。

## Global Verification Strategy

- UnitTestCore：`pytest -q`（目前 62 項基線）。
- `ruff check .`。
- `python -O` 契約冒煙（防火牆不可被 -O 繞過）。
- 決定論回歸：同 seed 兩次 `run_scenario` 的 `narrative_md` + `persona_samples` 相等。
- CLI 冒煙：`run` / `verify`（需 `$env:PYTHONPATH='src'`）。

## Baseline（完成基線，非本階段範圍）

已完成的 code-review 硬化（12 項，見 `HANDOFF.md §2`）+ 消除資料夾套娃 +
pyproject description 更新。git：branch `master`，尚未 commit。
