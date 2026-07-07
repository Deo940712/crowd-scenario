# Beacon Backlog

Backlog is non-executable. Promote work through PLAN, PART DESIGN, PART TODO, and CURRENT before implementation.

All items below have been promoted to PART DESIGN + TODO (status: designed, not yet
executed). See PLAN.md PARTs table. Promotion mapping:
- backlog-001 → part-004 (storylines)
- backlog-002 → part-003 (swing bug)
- backlog-003 → part-006 (voice variants)
- backlog-004 → part-005 (real-data example)
- backlog-005 → part-007 (misc enhancements)

## Items

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
