# part-009 TODO

Design authority: `.beacon/parts/part-009/DESIGN.md`

## SLICE Map

### part-009-slice-001: Adversarial corpus + regression lock

Status: done — archived at `.beacon/done/part-009/part-009-slice-001-done-current.md`

Goal:
建立 must_reject / must_allow corpus（按威脅模型 T1–T7 分類），先跑出現況掃描器的
真實通過率——**先量測、後修補**。

Candidate scope:
- [ ] `tests/firewall_corpus/must_reject.txt`（T1/T2/T3/T6 各 5–10 案例，`#` 注釋分類）。
- [ ] `tests/firewall_corpus/must_allow.txt`（T7 合法條件式 + 兩 pack 全部 voices）。
- [ ] `tests/test_firewall_adversarial.py`：corpus 參數化測試（此時 must_reject 預期部分失敗＝紅燈基線）。
- [ ] 記錄現況通過率到 slice 完成快照（哪些類別現在攔得住/攔不住）。

Forbidden scope:
- 改掃描器（屬 slice-002）。
- T4/T5 案例放進 must_reject（它們是已接受的限制，不是目標）。

Verification target:
- Unit: corpus 測試可跑、must_allow 全過（現況不誤殺）
- Regression: `pytest -q` 既有全綠

Done gate:
- corpus 涵蓋 T1–T3/T6/T7、現況通過率有紀錄。

### part-009-slice-002: Scanner hardening (normalize + patterns)

Status: done — archived at `.beacon/done/part-009/part-009-slice-002-done-current.md`

Goal:
修可修的類別：NFKC 正規化 + 零寬字元剝除（T1/T2）、中文數字＋單位 pattern（T3）、
injection 標記詞（T6）。must_reject corpus 全綠、must_allow 零誤殺。

Candidate scope:
- [ ] `firewall.py`：掃描前正規化 pass（`unicodedata.normalize("NFKC")` + 去零寬/分隔符）。
- [ ] `firewall.py`：中文數字＋單位 pattern（帶單位錨點，避免「十分看好」誤殺）。
- [ ] `firewall.py`：injection 標記詞清單。
- [ ] corpus 測試全綠 + 兩 pack voices 零誤殺回歸。

Forbidden scope:
- ML/LLM 分類器。
- 攔 T4/T5（規則式做不到，不硬做）。

Verification target:
- Unit: `pytest tests/test_firewall_adversarial.py -q` 全綠
- Regression: `pytest -q` 全綠（含 `test_deterministic_narrative_is_clean`）

Done gate:
- must_reject 全攔、must_allow 全放、既有測試零回歸。

Dependencies: slice-002 依賴 slice-001。

### part-009-slice-003: Two-layer security claim in docs

Status: done — archived at `.beacon/done/part-009/part-009-slice-003-done-current.md`

Goal:
把 README（英+中）的防火牆宣稱改為兩層表述：結構性契約是主防線；掃描器是
defense-in-depth，明確列出 T4/T5 為已知限制。

Candidate scope:
- [ ] README.md + README.zh-TW.md firewall 段落改寫（兩層表述 + limitations）。
- [ ] `references/firewall.md` 同步 threat model 摘要。

Forbidden scope:
- 過度弱化宣稱（結構層的保證仍然是硬的，照實寫）。

Verification target:
- Manual QA: 文件審閱——宣稱與 corpus 實測結果一致。

Done gate:
- 文件宣稱可被 corpus 測試背書，限制誠實列出。

Dependencies: slice-003 依賴 slice-002（先知道修完後的真實邊界才能寫）。
