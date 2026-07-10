# Beacon Backlog

Backlog is non-executable. Promote work through PLAN, PART DESIGN, PART TODO, and CURRENT before implementation.

Phase 1 items (001–005) are all DONE and archived. Phase 2 work is designed as
part-008..013 (see PLAN.md). Open backlog items start at backlog-006.

## Open Items

### backlog-008: HTML 報告 divergence panel + case-study 批次模式

Type: idea
Status: triage (deferred from part-011 slice-002)

Summary:
`tools/report.py` 的核心（3×2 sweep 網格）已於 part-011 slice-001 完成。兩個增強留待：
(1) `--posture {negative,neutral,positive}` → 在報告加 divergence 區塊（bucket +
storylines 全文）；(2) `--all-cases` 對 part-010 三案例批次產報告。皆非阻塞。

Promotion required before execution:
- PLAN update / PART DESIGN update / PART TODO SLICE / CURRENT promotion

### backlog-006: 文件「沒有任何數字離開引擎」宣稱過強

Type: design-debt
Status: DONE → part-009 slice-003（兩份 README + firewall.md 宣稱精確化，archived）

Summary:
README（英+中）宣稱「no number ever leaves / 沒有任何數字離開引擎」，但 emitted
artifacts 實際含：`rng_seed`、`n_personas`、`stance ∈ {-1,0,1}`、
`narrative_intensity ∈ {1,2,3}`、敘事編號。真正成立的保證是「**無決策等級的可加總
純量**（score/weight/modifier/expected return）、無原始市場數字」。應把兩份 README、
ASCII 圖說、`engine.py`/`contracts.py` docstring 的表述統一改精確：
- 不輸出決策等級的數值評分 / 可回寫的加權純量
- 不輸出 price/yield/return 等原始市場數字
- stance 等內部整數是有限集合的類別編碼，不是分數
建議併入 part-009 slice-003（兩層安全表述）一起改，或獨立小 PART。

### backlog-007: pack-defined categorical prior consensus model

Type: idea
Status: WON'T-DO (part-008 evaluation: neutral baseline did not over-neutralize; a pack
prior is unnecessary. Reopen only if a future domain shows over-neutralization.)

Summary:
part-008 的 Design Option C：讓 DomainPack 定義類別性 prior 當 persona baseline
（取代 hashed/neutral baseline）。語義最完整但增加 pack 複雜度與人工調參。
是否立案取決於 part-008 的 neutral-baseline 實驗結果（若 neutral 過度中性化則評估此案）。

## Archived Items (Phase 1, all DONE)

### backlog-001: NarrativeDivergence.storylines 是死欄位

Type: design-debt
Status: DONE → part-004 (implemented counterfactual storylines, archived)

Summary:
`contracts.py` 定義了 `NarrativeDivergence.storylines` 但 `compose_divergence` 從未填它，
永遠是空 tuple。要嘛實作（HIGH divergence 時產「群眾對/你錯」反事實敘事，契合排練定位），
要嘛刪掉。半成品欄位比沒有差。

### backlog-002: swing 排序 = intraday 別名

Type: bug
Status: DONE → part-003 (fixed, archived in .beacon/done/part-003/)

Summary:
`engine.py::_reaction_chain` 用 `reverse=bias >= 0`，swing 的 bias=0.0 → 排序方向與
intraday 完全相同（快跟風者先動）。swing 名義是中間態卻是 intraday 的別名。應給 swing
明確的中間行為，並用測試鎖三 horizon 排序確實不同。

### backlog-003: 敘事多樣性（每 persona/stance 只有一句 canned voice）

Type: idea
Status: DONE → part-006 (voice variants + intensity-scaled chain, archived)

Summary:
每個 persona 每個 stance 只有一句固定 voice → 同 stance 組合的敘事逐字相同。可每 stance
提供 2-3 句變體，由 seed hash 決定選哪句（仍 byte-stable）；反應鏈長度可隨 intensity 伸縮。

### backlog-004: 真實資料接入 worked example

Type: test-gap
Status: DONE → part-005 (worked example + docs, archived)

Summary:
文件缺「如何安全把真實輿情分數餵進 bucket 軸」的範例。防火牆架構本就支援（原始分數在
`make_seed` 就死掉），缺的只是 worked example + 文件。使用者最想做的事。

### backlog-005: 雜項增強

Type: idea
Status: DONE → part-007 (schema_version/sweep/property/PyPI done; codegraph N/A)

Summary:
- `CrowdNarrative` 加 `schema_version`（序列化存檔後的升級路徑）。
- `run --sweep`（一次跑 3 horizon × 2 intensity 的對照表）。
- property-based 測試（hypothesis）：決定論、bucket 單調性、任意 pack 防火牆不變量。
- 發佈 PyPI（0.1.0、zero-dep、測試齊全，成本低）。
- 重建 `.codegraph` 索引（搬移套娃後舊索引路徑失效）。

Promotion required before execution (all items):
- PLAN update / PART DESIGN update / PART TODO SLICE / CURRENT promotion
