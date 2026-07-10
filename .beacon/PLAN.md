# Beacon Plan

## Project Goal

crowd-scenario：deterministic、firewalled、domain-pluggable 的群眾情境**排練**器
（rehearsal，非 forecast）。讀 bucketed `ScenarioSeed`，只吐 categorical
`crowd_consensus ∈ {negative,neutral,positive}` + 敘事——**不輸出任何決策等級的
可加總純量**（score/weight/modifier/原始市場數字）。

**本階段目標（Phase 2：可信度與證據期）**：從功能建設轉向證據建設——
對抗性驗證安全邊界、以實驗選擇共識模型、累積真實案例、建立視覺展示、
證明跨領域通用性。目標是把「聰明的技術原型」變成「可信、限制明確、
有證據的作品」。

## Non-goals

- 不做真實預測/回測（定位是排練，不是 forecast；case studies 不是準確率宣稱）。
- 不新增任何 runtime 依賴到引擎 core（`dependencies = []` 是刻意的）。
- 不引入決策等級純量到 emitted artifact（防火牆紅線）。
- 未經 part-008 證據，不改 public default consensus_mode。
- 不把 regex 掃描器包裝成完整語義安全系統（它是 defense-in-depth，結構契約才是主防線）。

## PARTs

### Phase 1 — 已完成（功能建設期）

| PART | Status | Goal | Design | TODO |
| --- | --- | --- | --- | --- |
| part-001 | done (slices 001+002) | 共識可回應情境語義（aggregate 模式）+ CLI 接線 | `.beacon/parts/part-001/DESIGN.md` | `.beacon/done/part-001/` |
| part-002 | done (slice-001) | CLI 可輸入自訂 metrics（`--metrics`） | `.beacon/parts/part-002/DESIGN.md` | `.beacon/done/part-002/` |
| part-003 | done (slice-001) | 修 swing 排序 = intraday 別名 bug | `.beacon/parts/part-003/DESIGN.md` | `.beacon/done/part-003/` |
| part-004 | done (slice-001, chose B) | storylines 反事實敘事實作 | `.beacon/parts/part-004/DESIGN.md` | `.beacon/done/part-004/` |
| part-005 | done (slice-001) | 真實資料接入 worked example + 文件 | `.beacon/parts/part-005/DESIGN.md` | `.beacon/done/part-005/` |
| part-006 | done (slices 001+002) | 敘事多樣性（voice variants + intensity 伸縮） | `.beacon/parts/part-006/DESIGN.md` | `.beacon/done/part-006/` |
| part-007 | done (4 slices + 1 N/A) | 雜項增強（schema_version/sweep/property/PyPI） | `.beacon/parts/part-007/DESIGN.md` | `.beacon/done/part-007/` |

### Phase 2 — 已設計，待 promote（可信度與證據期）

| 優先 | PART | Status | Goal | Design | TODO |
| --- | --- | --- | --- | --- | --- |
| P1 | part-009 | done (slices 001–003) | 對抗性防火牆驗證（threat model + corpus + 兩層安全表述） | `.beacon/parts/part-009/DESIGN.md` | `.beacon/done/part-009/` |
| P1 | part-008 | done (4 slices) | 共識模型評估（推薦 aggregate_neutral；執行 gated 至 part-013） | `.beacon/parts/part-008/DESIGN.md` | `.beacon/done/part-008/` |
| P2 | part-010 | done (3 slices) | 三個真實 case studies（含「哪裡不能信」必填段） | `.beacon/parts/part-010/DESIGN.md` | `.beacon/done/part-010/` |
| P2 | part-011 | done (slices 001+003; 002 deferred) | 靜態 HTML comparison report（3×2 sweep 網格） | `.beacon/parts/part-011/DESIGN.md` | `.beacon/done/part-011/` |
| P3 | part-012 | done (2 slices) | 第三 DomainPack：software migration（非金融） | `.beacon/parts/part-012/DESIGN.md` | `.beacon/done/part-012/` |
| P4 | part-013 | done (2 slices) | default 遷移至 aggregate_neutral（0.2.0，已執行） | `.beacon/parts/part-013/DESIGN.md` | `.beacon/done/part-013/` |

建議執行順序：009 → 008 → 010 → 011 → 012 → 013。
（009/008 可互換；010 的 hashed/aggregate 對照資料可餵 008 的評估矩陣。）

### Phase 3 — 結構性防火牆補強（契約硬化期）

| 優先 | PART | Status | Goal | Design | TODO |
| --- | --- | --- | --- | --- | --- |
| P1 | part-014 | in-progress (slice-001 active) | 補強公開契約與 DomainPack，使 firewall 違規物件無法建構/被改壞（規劃+雙路審查：`.omo/plans/structural-firewall-hardening.md`） | `.beacon/parts/part-014/DESIGN.md` | `.beacon/parts/part-014/TODO.md` |

## Success Criteria（Phase 2）

- 防火牆宣稱與 corpus 實測一致：must_reject 全攔、must_allow 零誤殺、
  T4/T5 限制誠實文件化。
- 共識模型 default 的選擇有可審查的證據（評估矩陣 + 五準則對照），而非直覺。
- 三份 case study 可離線重現，且每份都有「哪裡不能信」。
- 一條命令產出可展示的 HTML 對照報告。
- 第三個 domain pack 通過全部 pack-agnostic 測試 + 語義自檢。
- 全程維持：`pytest` 全綠、`ruff` clean、`python -O` 契約 enforced、決定論不破。

## Global Risks

- **評估變成先射箭再畫靶**：part-008 的 case matrix 必須先定案再跑，不得為了
  支持 aggregate 而挑案例。
- **case study 滑向行銷文**：模板強制「哪裡不能信」必填段 + 條件式語氣。
- **掃描器正規化誤殺合法 persona 語音**：all-pack-voices 零誤殺回歸鎖。
- **default 遷移的 golden 漂移面大**：part-013 gate + 影響面盤點 slice 先行。
- **文件宣稱過強**（見 backlog-006）：所有新文件用「無決策等級可加總純量」表述，
  不用「沒有任何數字」。

## Global Verification Strategy

- UnitTestCore：`pytest -q`（目前 117 項基線）。
- `ruff check .`。
- `python -O` 契約冒煙（防火牆不可被 -O 繞過）。
- 決定論回歸：同 seed 兩次 `run_scenario` 完整 artifact 相等。
- CLI 冒煙：`run` / `verify` / `--sweep`（需 `$env:PYTHONPATH='src'`）。
- Phase 2 新增：corpus 測試（part-009）、評估矩陣重現（part-008）、
  case study 重現（part-010）、報告決定論（part-011）。

## Baseline

Phase 1 全部完成並歸檔於 `.beacon/done/part-001..007/`。
git：branch `main`，已 push 至 GitHub（1cc1462）。
`pytest -q` → 117 passed；`ruff` clean；`twine check` PASSED。
