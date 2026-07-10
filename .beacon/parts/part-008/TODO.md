# part-008 TODO

Design authority: `.beacon/parts/part-008/DESIGN.md`

## SLICE Map

### part-008-slice-001: Lock current consensus models

Status: done — see `.beacon/done/part-008/`

Goal:
先鎖住 `hashed` 與 current `aggregate` 的既有輸出，避免評估實驗改壞現況。

Candidate scope:
- [ ] 參數化 representative seeds，pin explicit hashed/current aggregate。
- [ ] 確認不指定 mode 的現行 default，文件化但不改。

Forbidden scope:
- 改 default。
- 改 stance 公式。

Verification target:
- Unit: focused engine tests
- Regression: `pytest -q`、`ruff check .`

Done gate:
- 現有兩模式被 golden tests 鎖住。

### part-008-slice-002: Experimental neutral-baseline aggregate

Status: done — see `.beacon/done/part-008/`

Goal:
加入 experimental neutral-baseline aggregate，供比較而非直接成為 default。

Candidate scope:
- [ ] 以 neutral consensus 作 persona baseline，再 majority aggregate。
- [ ] 模式名稱與 API 明確標示 experimental（命名在實作前定案）。
- [ ] 決定論 / 防火牆 / no-hash-direction 測試。

Forbidden scope:
- 改 public default。
- 加 emitted scalar。

Verification target:
- Unit: neutral-baseline tests
- Regression: existing modes byte-stable

Done gate:
- 實驗模式可重現，且 top-level direction 不受 hashed baseline 影響。

Dependencies: slice-002 依賴 slice-001。

### part-008-slice-003: Build consensus comparison matrix

Status: done — see `.beacon/done/part-008/`

Goal:
對兩個 packs 的正向/負向/中性案例跑三模型比較，產出可審查矩陣。

Candidate scope:
- [ ] 定義固定 case corpus。
- [ ] 記錄 consensus / majority agreement / neutral stability / determinism。
- [ ] 產出 `.beacon/done/part-008/consensus-evaluation.md` 草稿。

Forbidden scope:
- 將案例矩陣稱為回測或準確率。

Verification target:
- 每個 case 可重跑並產生相同矩陣。

Done gate:
- 矩陣涵蓋兩 domain、三方向、三模型。

Dependencies: slice-003 依賴 slice-002。

### part-008-slice-004: Default recommendation decision

Status: done — recommend aggregate_neutral; execution gated to part-013. See `.beacon/done/part-008/consensus-evaluation.md`

Goal:
依矩陣決定推薦 default：維持 hashed / current aggregate / neutral aggregate / 暫不變更。

Outcome:
一份 go/no-go 決策，含限制、migration 影響與後續 PART 建議。

Forbidden scope:
- 本 slice 不改 code/default。

Verification target:
- 決策逐條對應 DESIGN 的五項準則。

Done gate:
- `consensus-evaluation.md` 完整，並明確指向 part-013 是否應執行。
