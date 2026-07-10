# part-014 TODO

Design authority: `.beacon/parts/part-014/DESIGN.md`
Work plan (executor detail): `.omo/plans/structural-firewall-hardening.md`

## SLICE Map

### part-014-slice-001: Contract hardening (contracts.py)

Status: planned

Goal: 讓 `ScenarioSeed`/`PersonaReaction`/`CrowdNarrative`/`NarrativeDivergence`
無法在 firewall 違規狀態下被建構。

Outcome: 直接建構公開 dataclass 也不能繞過防火牆。

Candidate scope:
- [ ] `ScenarioSeed.ordinal_context` 拒絕非字串 key/value(TDD)
- [ ] `PersonaReaction.__post_init__`:stance∈{-1,0,1}(排除 bool)、is_synthetic is True、字串欄位非空(TDD)
- [ ] `CrowdNarrative` + `NarrativeDivergence` 硬鎖 `synthetic_population is True`(TDD)

Forbidden scope:
- domains/、cli.py、composer.py、engine.py、任何 schema 欄位變更

Verification target:
- Unit: `pytest tests/test_contracts.py -q`
- Regression: `pytest -q`;`python -O -m pytest tests/test_contracts.py -q`;`ruff check .`
- Manual QA: `python -c` 建構違規物件印出 ContractError

Done gate:
- 三個違規類別各有 fail-then-pass 測試;全套綠;`python -O` 契約綠;歸檔 + promote slice-002

### part-014-slice-002: DomainPack immutability + finite validation (domains/base.py)

Status: planned

Goal: 已驗證的 pack 不能被改壞;NaN/inf/bool 被拒;`voice_variants` stance key 限界。

Outcome: 合法 pack 建構後無法被修改成非法狀態。

Candidate scope:
- [ ] `validate_pack` 拒絕 tilt/herding/sensitivity 的非 finite 與 bool(TDD)
- [ ] `validate_pack` 限 `voice_variants` stance key ∈ {-1,0,1}(TDD)
- [ ] `DomainPack.__post_init__` + `Axis.__post_init__` 以 MappingProxyType 深度凍結(TDD)
- [ ] 凍結後 byte-compare 三 domain 決定論

Forbidden scope:
- contracts.py、cli.py、composer.py、engine.py;pack 建構點;數值範圍限制

Verification target:
- Unit: `pytest tests/test_contracts.py tests/test_engine.py -q`
- Regression: `pytest -q`;`ruff check .`;LSP src/ = 0;`python -O -m pytest tests/test_contracts.py -q`
- Manual QA: 決定論 byte-compare vs `.omo/evidence/baseline-*.json`

Done gate:
- mutation 測試 raise TypeError;三 domain 輸出 byte-identical;全套綠;歸檔 + promote slice-003

### part-014-slice-003: Boundary hardening (cli.py + composer.py)

Status: planned

Goal: CLI `--metrics` 與 `compose_divergence` 對非法輸入回傳一致乾淨錯誤。

Outcome: 公開邊界對非法輸入不再 traceback / KeyError。

Candidate scope:
- [ ] `_parse_metrics` 驗證 finite 數值,乾淨 exit 2(TDD)
- [ ] `compose_divergence` 前置 `ContractError` guard(TDD)
- [ ] 擴充 `tests/test_cli.py`:metrics/sweep/fallback 整合覆蓋

Forbidden scope:
- contracts.py、domains/、engine.py;consensus/schema 變更

Verification target:
- Unit: `pytest tests/test_composer.py tests/test_cli.py -q`
- Regression: `pytest -q`;`ruff check .`
- Manual QA: `main([...])` in-process bad metrics 回 2、空 stdout、單行 `error:`

Done gate:
- 所有邊界測試綠;全套綠;歸檔 + promote slice-004

### part-014-slice-004: Full verification + docs calibration

Status: planned

Goal: 全面驗證 + 文件校準 + 歸檔 part-014。

Outcome: 專案實作與 README 結構性宣稱一致,證據齊備。

Candidate scope:
- [ ] 全套驗證:pytest / ruff / `python -O` / LSP / determinism / report.py
- [ ] README(英+中)+ docstring claim 校準(僅在證實不準確時改)
- [ ] 寫 `verification-report.md`;PLAN 標 part-014 done;CURRENT 回 planning-only

Forbidden scope:
- 任何 src 變更(除非文件校準本身不需改 src);backlog 其他工作

Verification target:
- Unit: `pytest -q`
- Regression: 全部 verification target 綠 + byte-compare 決定論
- Manual QA: 新 shell 實跑 CLI happy+failure

Done gate:
- 全部檢查綠;claim checklist 記錄;part-014 歸檔;CURRENT planning-only
