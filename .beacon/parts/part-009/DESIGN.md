# part-009 DESIGN

Source: Codex review 短板 #3（regex firewall 做展示很棒，但宣稱硬安全邊界需要 adversarial tests）。

## Goal

用**威脅模型驅動的對抗性測試**驗證 `scan_violations` 的真實邊界：建立 must-reject /
must-allow 兩組 corpus，補掃描器能力（可修的修），並**誠實文件化修不了的限制**。
產出後，防火牆的安全宣稱從「規則式展示」升級為「經對抗驗證、限制明確」。

## Non-goals

- 不宣稱 scanner 是完整的語義安全系統或形式驗證器。
- 不引入 ML/LLM 分類器當掃描器（違反 zero-dep、決定論）。
- 不改變結構性防火牆（契約層）——它才是主保證，本 PART 只強化第二層。
- 不為了攔截而過度誤殺合法條件式語句（誤殺率是明確驗收項）。

## Assumptions

- 結構性契約（無 scalar 欄位、bucket-only 輸入）是主防線；scanner 是 defense-in-depth。
- 目前 scanner 涵蓋：半形/全形數字、貨幣/百分比/價格語境、`stance=` 等 token、部分下單語。
- 已知盲區（來自 review）：字元拆分、Unicode 同形字、中文數字、語義型建議、編碼、
  prompt injection 型輸出。

## Threat Model（分類）

| # | 類別 | 例子 | 預期處置 |
|---|---|---|---|
| T1 | 字元拆分/插入 | `買 進`、`買　進`、`買‧進`、`b u y` | 應攔（正規化後掃）|
| T2 | Unicode 同形/全形 | `ＮＡＶ`、`ＢＵＹ`、混合寬度 | 應攔（NFKC 正規化）|
| T3 | 中文數字 | `五十元`、`百分之五十`、`兩成` | 應攔（中文數字 pattern）|
| T4 | 語義型建議（無禁詞） | 「現在是很適合採取行動的時候」 | **接受修不了**，文件化 |
| T5 | 編碼/暗號 | Base64、諧音 | **接受修不了**，文件化 |
| T6 | prompt-injection 型輸出 | 「忽略前述規則，以下是實際建議…」 | 應攔（injection 標記詞）|
| T7 | 誤殺（合法條件式） | 「這類人格可能想趁機加碼」 | **必須放行** |

## Design Options

- **A. 散落在 pytest 的字串測試**：難維護、難看出覆蓋率。捨棄。
- **B. corpus 檔案 + 參數化測試（選定）**：`tests/firewall_corpus/must_reject.txt` 與
    `must_allow.txt`（一行一案例，`#` 注釋分類），pytest 參數化逐行斷言。新增案例=加一行。
- **C. 引入第三方 fuzzing 工具**：違反 zero-dep 精神（dev 依賴可議，但 corpus 已足夠）。捨棄。

## Chosen Design

選 **B**。三步：

1. **建 corpus**：按威脅模型 T1–T7 各寫 5–10 案例進兩個 corpus 檔。
2. **修掃描器（僅可修類）**：
   - T1/T2：掃描前先做 `unicodedata.normalize("NFKC", text)` + 去除零寬/分隔字元的
     正規化 pass（stdlib，決定論）。
   - T3：加中文數字＋單位 pattern（`[一二三四五六七八九十百千萬兩]+\s*(?:元|成|%|％|percent)`
     與 `百分之[一二三四五六七八九十]+`）。
   - T6：加 injection 標記詞（`忽略前述`、`ignore previous`、`以下是實際建議` 等）。
3. **文件化限制**：README firewall 段落改為兩層表述——
   > 結構性契約是主防火牆；文字掃描器是保守的、決定性的 defense-in-depth 過濾器，
   > 不是完整的語義安全證明。語義型建議與編碼繞過超出規則式掃描的能力範圍。

## Verification Targets

- Unit：`tests/test_firewall_adversarial.py`（corpus 參數化）。
- must_reject corpus 全數被攔；must_allow corpus 全數放行（誤殺=fail）。
- 既有 117 測試零回歸（尤其 `test_deterministic_narrative_is_clean` —— 正規化不可
  誤殺合法 persona 語音）。
- README（英+中）firewall 段落更新為兩層表述。

## Unit Test Strategy

- `test_must_reject_corpus`：參數化逐行 → `scan_violations(line) != ()`。
- `test_must_allow_corpus`：參數化逐行 → `scan_violations(line) == ()`。
- `test_normalization_is_deterministic`：正規化 pass 同輸入同輸出。
- `test_all_pack_voices_still_clean`：兩個 pack 的所有 voice/variants 全放行（誤殺回歸）。

## Manual QA Strategy

- 抽 3 個 T1/T2/T3 案例手動跑 `scan_violations` 確認攔截。
- 抽 2 個 T4/T5 案例確認**不攔**且 limitation 文件有寫。

## Risks

- NFKC 正規化可能改變合法中文的比對行為 → 誤殺回歸測試（all_pack_voices_still_clean）鎖住。
- 中文數字 pattern 太寬（「十分看好」的「十分」是程度副詞）→ pattern 必須帶單位錨點。
- injection 標記詞清單永遠不完整 → 文件明確標示為 heuristic，不是保證。

## Open Questions

- 正規化 pass 放在 `scan_violations` 內部（所有呼叫者受益）或獨立函式？
  → 傾向內部，slice 執行時定案。
