# part-008 DESIGN

Source: Codex review + internal review（hashed default 反直覺，但 current aggregate 仍受 hashed baseline 影響）。

## Goal

評估並選擇可解釋的 consensus model；**不預設 aggregate 一定成為 default**。比較三種模型：

1. `hashed`：seed hash 直接決定 top-level consensus。
2. `aggregate_current`：hashed baseline → persona stance → majority（目前的 `aggregate`）。
3. `aggregate_neutral`：neutral baseline → ordinal/persona stance → majority（實驗模式）。

用固定案例矩陣與明確決策準則，產出「推薦 default / 保留現況 / 尚無足夠證據」結論。

## Non-goals

- 本 PART 不直接更改 public default。
- 不宣稱任何模式具備預測力或回測優勢。
- 不新增數字純量到 emitted artifacts。
- 不引入 domain prior 模型；若 neutral-baseline 表現不足，另開後續設計。

## Assumptions

- 目前 `aggregate` 並非純情境聚合：`_stance_for` 的 baseline 仍來自 hashed consensus。
- hashed/current aggregate 已有決定論與回歸測試。
- 評估目標是語義一致性、可解釋性與穩定性，不是預測準確率。

## Design Options

- **A. 直接把 current aggregate 設 default**：實作快，但未解決 hash 對 persona baseline 的污染；捨棄。
- **B. 三模型實驗比較（選定）**：實作 neutral-baseline experimental mode，建立案例矩陣，再決定 default。
- **C. 立即加 DomainPack prior**：可表達 domain 基準，但增加人工調參與 pack 複雜度；留作未來選項。

## Chosen Design

選 **B**。

評估矩陣至少包含：

- STOCK_TW：深折價＋高殖利率、溢價＋低殖利率、中性桶。
- PRODUCT_LAUNCH：漲價且價值不足、價值提升且價格持平、切換成本高的中性場景。
- 每個情境跑三種 horizon × 兩種 intensity（可使用現有 sweep）。

每一格記錄：

- consensus model / crowd consensus
- persona stance distribution（只做測試內部統計，不新增 emitted scalar）
- consensus 是否與 persona majority 一致
- 同輸入決定論
- 是否出現「明確 buckets 卻反直覺 consensus」

決策準則：

1. 可解釋性：共識能從 buckets + personas 說明，而非只能說「hash 如此」。
2. 語義一致性：明確方向情境與人格多數不應相反。
3. 中性穩定性：中性/弱訊號情境不應頻繁極化。
4. 決定論與防火牆不變量保持。
5. 不以「符合預期答案」硬編碼 case-specific 分支。

## Verification Targets

- Unit：三模式決定論；neutral-baseline 模式只由 ordinal/persona 反應決定。
- Evaluation：生成固定 comparison matrix（JSON/Markdown test fixture 或報告）。
- Regression：hashed 與 current aggregate byte-stable。
- Decision report：寫入 `.beacon/done/part-008/consensus-evaluation.md`，含 go/no-go 結論。

## Unit Test Strategy

- `test_neutral_baseline_aggregate_is_deterministic`
- `test_neutral_baseline_aggregate_ignores_hashed_direction`
- `test_explicit_hashed_and_current_aggregate_unchanged`
- 參數化 case matrix（兩個現有 packs × 代表情境）。
- 不把模型比較用的 persona net scalar加到公開 artifact。

## Manual QA Strategy

CLI 或 evaluation script 列出同一情境的三模型對照；人工檢查反直覺案例與中性穩定性。

## Risks

- neutral baseline 可能讓 momentum personas 大量 neutral，削弱群眾鏈條。
- case matrix 太小會讓 default 決策偏誤；必須涵蓋正向、負向、中性、兩個 domain。
- 評估報告不可包裝成回測或 market accuracy。

## Open Questions

- `aggregate_neutral` 是否只作 experimental mode，或成為正式 API mode？由 slice-002 實驗結果決定。
- 若 neutral baseline 過度中性，是否開新 PART 評估 pack-defined categorical prior？
