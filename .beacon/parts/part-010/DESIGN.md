# part-010 DESIGN

Source: 內部評估「下一階段應從 feature building 轉向 evidence building」+ Codex review
（「幾個真實 case study 會讓它從聰明的技術原型變成很有說服力的作品」）。

## Goal

建立**三個完整、可重現的 case study**，每個都誠實展示引擎「哪裡有用、哪裡不能信」。
這是證據建設，不是功能建設——產出是文件 + 可執行 script，不是新引擎能力。

## Non-goals

- 不做回測、不宣稱預測準確率（case study 展示的是排練過程與可解釋性，不是 hit rate）。
- 不接真實即時 API（輸入是手工整理的歷史情境快照，離線、可重現）。
- 不為了讓 case study「好看」而調引擎參數（發現問題就如實記錄，必要時開 incident/PART）。

## Assumptions

- 引擎能力已齊：`--metrics`、`--sweep`、`--consensus-mode`、divergence storylines。
- part-008 可能尚未完成——case study 同時展示 hashed 與 aggregate，正好為 part-008
  的評估矩陣提供素材（兩個 PART 互補，順序不互鎖）。
- case study 的原始數字只出現在「輸入」段，經 bucket 後不再出現（自我示範防火牆）。

## 三個案例（涵蓋兩個現有 domain + 一個延伸情境）

1. **CASE A（STOCK_TW）：ETF 深折價＋高殖利率**
   原型情境：高股息 ETF 除息後折價擴大（如 0056 型情境）。
   看點：aggregate 共識與 persona 多數方向一致；hashed 對照顯示骰子問題；
   horizon sweep 顯示誰先動的差異。

2. **CASE B（PRODUCT_LAUNCH）：漲價但價值提升不足**
   原型情境：SaaS 產品漲價 30%、新功能感知價值低（price_hike 型情境）。
   看點：重度用戶 vs 免費用戶 vs 精打細算族的分歧；divergence storylines
   （假設 PM 自己的判讀是 positive，與群眾 negative 對比 → HIGH divergence 反事實）。

3. **CASE C（STOCK_TW 反向情境）：溢價＋低殖利率的追高**
   原型情境：熱門 ETF 溢價 1.4%、殖利率 3.1%（00878 型情境）。
   看點：中性/偏空情境下的群眾行為；恐慌散戶與 PTT 風向的 voice variants；
   severe intensity 的鏈條展開。

每個 case study 的固定結構（誠實模板）：

```
1. 情境背景（一段話，含免責：合成排練、非預測）
2. 輸入：raw metrics → buckets（明確展示數字在哪裡消失）
3. personas 反應（stance 分布 + 代表語音）
4. hashed vs aggregate 對照（含說明兩者為何可能不同）
5. horizon × intensity sweep（6 格表）
6. divergence：對照一個假想的「你自己的判讀」→ storylines
7. 哪裡有用（What this told us）
8. 哪裡不能信（What this CANNOT tell us）← 必填，不可省略
```

## Design Options

- **A. 純 Markdown 文件**：好讀但無法驗證可重現。捨棄。
- **B. Markdown + 可執行 script（選定）**：`case_studies/case_a.md` 敘事 +
    `case_studies/run_case_a.py`（或單一 `run_all.py`）重現所有輸出；測試斷言 script
    輸出與文件中的關鍵結論一致（consensus 方向、divergence bucket）。
- **C. Jupyter notebook**：引入依賴、diff 不友善。捨棄。

## Chosen Design

選 **B**。目錄 `case_studies/`（與 `examples/` 分開——examples 是 API 用法示範，
case_studies 是證據文件）。一個共用 runner + 三份 case 文件。測試只鎖「可重現性」
（script 跑兩次相同、關鍵結論與文件一致），不鎖全文。

## Verification Targets

- `case_studies/run_all.py` 可離線執行、決定論（跑兩次 byte-identical）。
- `tests/test_case_studies.py`：每個 case 的 consensus 方向 / divergence bucket 與
  文件宣稱一致。
- 每份 case 文件含「哪裡不能信」段落（測試檢查段落存在）。
- 原始數字不出現在 script 輸出的敘事部分（防火牆自我示範）。

## Unit Test Strategy

- `test_case_studies_are_reproducible`：run 兩次比對。
- `test_case_conclusions_match_docs`：關鍵結論（三個 case 的 aggregate 方向）與文件
  front-matter 一致。
- `test_case_docs_have_limitations_section`：每份 md 含「不能信」段落標題。

## Manual QA Strategy

人工閱讀三份 case study：敘事通順、結論誠實、免責齊全、無過度宣稱。

## Risks

- case study 寫成行銷文 → 模板強制「哪裡不能信」為必填段。
- 用詞滑向預測（「群眾將會…」）→ 全程條件式語氣，過 scan_violations 抽查。
- 與 part-008 評估矩陣重工 → case study 的 hashed/aggregate 對照數據可直接餵給
  part-008，執行順序上先做哪個都可以。

## Open Questions

- case_studies/ 是否進 PyPI wheel？→ 否（同 examples/，只留 repo）。
- 中文或英文撰寫？→ 建議中文為主（目標讀者）+ 英文摘要，slice 執行時定案。
