# part-015 TODO

Design authority: `.beacon/parts/part-015/DESIGN.md`
Work plan (executor detail): `.omo/plans/definance-crowd-scenario.md`

## SLICE Map

### part-015-slice-001: scenario_label rename + alias (seed.py)

Status: done → `.beacon/done/part-015/part-015-slice-001-done-current.md`

Goal: `make_seed` 改用 `scenario_label`,舊名保留 deprecated keyword-only alias。

Outcome: 新舊參數路徑皆可用;衝突拋 TypeError;決定論不變。

Candidate scope:
- [ ] seed.py 簽名演進 + alias 解析 + DeprecationWarning(TDD)
- [ ] 內部呼叫者改新名:cli.py:138,200、examples/real_data.py:48
- [ ] C1 後三 domain byte-compare

Forbidden scope:
- ScenarioSeed 欄位名;engine.py;domains/;composer.py

Verification target:
- Unit: `pytest tests/test_seed.py tests/test_contracts.py -q`(檔名依實際建立調整)
- Regression: `pytest -q`;`ruff check .`
- Manual QA: 新舊參數路徑 `python -c` 驗證

Done gate:
- alias 測試 fail-then-pass;byte-compare IDENTICAL x3;歸檔 + promote slice-002

### part-015-slice-002: pack-overridable register + intensity_display (base.py + engine.py)

Status: planned

Goal: 把 `register` 與 intensity 顯示詞從 engine 硬編碼移到 DomainPack。

Outcome: 非中文 domain 可自訂;三個現有 pack 輸出 byte-identical。

Candidate scope:
- [ ] base.py 新欄位 + validate + deep-freeze(TDD)
- [ ] engine.py 讀 pack.register / pack.intensity_display(TDD)
- [ ] C2 後三 domain byte-compare

Forbidden scope:
- seed.py;cli.py;三個 pack 的實際值;EngineFacts 欄位名

Verification target:
- Unit: `pytest tests/test_engine.py tests/test_contracts.py -q`
- Regression: `pytest -q`;`ruff check .`;LSP src/ = 0;`python -O` 契約
- Manual QA: override pack 驗證 + byte-compare

Done gate:
- override 測試 fail-then-pass;byte-compare IDENTICAL x3;歸檔 + promote slice-003

### part-015-slice-003: docs de-finance (READMEs + docstrings)

Status: planned

Goal: README 主範例改非金融領先;shared-core docstring 中性化。

Outcome: 第一印象不再是股票工具;技術宣稱不變。

Candidate scope:
- [ ] README.md + README.zh-TW.md 範例重排(software_migration 領先)
- [ ] contracts.py / seed.py / base.py docstring 中性化

Forbidden scope:
- 任何程式行為;股票範例不得刪除(只降序)

Verification target:
- Unit: 無自動(docs);design-review gate
- Regression: `pytest -q`;`ruff check .`
- Manual QA: README 新首例指令實跑 exit 0

Done gate:
- 兩份 README 首例為 software_migration;docstring 含非金融例;歸檔 + promote slice-004

### part-015-slice-004: full verification + close

Status: planned

Goal: 全面驗證 + 歸檔 part-015。

Outcome: 全部 gate 綠、決定論證明、CURRENT 回 planning-only。

Candidate scope:
- [ ] pytest / ruff / python -O / LSP / 三 domain byte-compare / verify
- [ ] verification-report.md;PLAN 標 done;CURRENT 重置

Forbidden scope:
- 任何 src 變更

Verification target:
- Unit: `pytest -q`
- Regression: 全部 verification target
- Manual QA: 新 shell 新舊參數 + override 路徑

Done gate:
- 全綠 + byte-identical x3;part-015 歸檔;CURRENT planning-only
