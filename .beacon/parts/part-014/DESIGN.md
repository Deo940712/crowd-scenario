# part-014 DESIGN

Source: 專案健檢發現多個「公開 dataclass / DomainPack 可繞過 README 宣稱的結構性防火牆」
缺口。本 PART 把實作補強到與文件承諾一致——讓 firewall 違規物件**無法被建構、
無法被事後改壞**。規劃與雙路審查記錄於 `.omo/plans/structural-firewall-hardening.md`。

## Goal

關閉四類 firewall 契約缺口,使不論用何種方式建構,違規物件都被 `ContractError` /
`TypeError` 擋下,同時**所有既有合法行為 byte-identical 不變**:

1. `ScenarioSeed.ordinal_context` 只能帶 ordinal 字串(不能塞原始數字)。
2. `PersonaReaction` 與 `synthetic_population` flags 硬性驗證。
3. `DomainPack` 深度不可變 + finite-only 數值 + `voice_variants` stance key 限界。
4. CLI `--metrics` 與 `compose_divergence` 邊界一致的乾淨錯誤。

## Non-goals

- 不改 consensus 演算法、persona 文案、emitted schema 欄位。
- 不新增任何 runtime 依賴(stdlib only;`dependencies = []`)。
- 不對 pack 數值加範圍限制(herding∈[0,1] 等)——只要求 finite,範圍缺證據。
- 不重構 engine 主流程;只碰 todo 指名的檔案。
- 不用 `assert`(必須 survive `python -O`);不做 backlog 其他工作;不 git push。

## Assumptions

- `make_seed` 只產生 str→str 的 ordinal,故 ScenarioSeed 驗證不破壞任何合法呼叫者。
- engine 只**讀** pack(`.get`/`[]`),三個 shipped pack 用 dict literal 建構,深度凍結不影響建構點。
- (已驗證)`DomainPack` 現已不可雜湊、`MappingProxyType == dict` → 深度凍結不改相等性/雜湊。
- (已驗證)`json.loads` 接受 `NaN`/`Infinity` → 需 `math.isfinite`,單純型別檢查不夠。
- (已驗證)`tests/test_cli.py` 已存在(192 行,in-process `main()`+capsys,無 subprocess)。

## Design Options

- A(採用):在既有 `__post_init__` 加 `ContractError` guards + `MappingProxyType` 深度凍結。
  零依賴、與現有 `ScenarioSeed` 凍結手法一致(contracts.py:68-74 已有先例)。
- B(否決):新增外部 schema 驗證層(pydantic 等)——違反 zero-dependency 紅線。
- C(否決):把 pack 改成 namedtuple/全 tuple——大改建構點,風險高於收益。

## Chosen Design

逐 slice、TDD:先寫失敗測試 → 記錄失敗 → 最小修正 → 聚焦測試 → 全套回歸。

- slice-001 `contracts.py`:ordinal_context 字串驗證、PersonaReaction `__post_init__`、
  `synthetic_population` 硬鎖(mirror 既有 `non_authoritative` 檢查)。
- slice-002 `domains/base.py`:`validate_pack` finite/bool 檢查、`voice_variants` stance
  key 限界、`DomainPack.__post_init__` + `Axis.__post_init__` 以 `MappingProxyType` 深度凍結
  (`object.__setattr__`,frozen dataclass)。凍結後立即 byte-compare 決定論。
- slice-003 `cli.py` + `composer.py`:`_parse_metrics` finite 數值驗證(乾淨 exit 2)、
  `compose_divergence` 前置 `ContractError` guard;擴充 `tests/test_cli.py` 整合覆蓋。
- slice-004:全套驗證(pytest/ruff/`python -O`/LSP/determinism/report)+ 文件校準 + 歸檔。

## Verification Targets

- `pytest -q` 全綠(≥262 基線 + 新測試);`ruff check .` clean;LSP src/ = 0 diagnostics。
- `python -O -m pytest tests/test_contracts.py -q`(guards 不可被 -O 剝除)。
- 決定論:三 domain `run` 輸出 byte-identical 於 `.omo/evidence/baseline-*.json`。
- CLI 冒煙:`run` / `verify` / `--sweep`;`tools/report.py` 產 HTML exit 0。

## Unit Test Strategy

- contracts:各違規建構(raw number seed、stance=999/True、synthetic_population=False)raise ContractError;合法建構仍成立。
- domains:NaN/inf/bool 於 tilt/herding/sensitivity raise;`voice_variants` stance 999 raise;凍結後 mutation raise TypeError,讀取仍可。
- cli:`main([...])` in-process,bad metrics(str/null/bool/NaN/Infinity/array/malformed/missing-axis)回 2 + `error:` stderr + 空 stdout;`--sweep` 6 cells;unknown symbol fallback 回 0 + warning。
- composer:`compose_divergence(n, "sideways")` raise ContractError(非 KeyError)。

## Manual QA Strategy

- 新 shell 實跑 todo 10/12/13 的 CLI happy+failure 指令,確認輸出與 evidence 相符。
- `verify` 兩 domain 決定論 OK。

## Risks

- 深度凍結可能踩到隱性依賴 mutability 的程式/測試 → 獨立成 slice,凍結前抓基線、凍結後立即全套 + byte-compare;任何 diff 開 incident。
- `MappingProxyType` 型別註記漂移 → dict→Mapping 並跑 ruff/LSP。
- 決定論被驗證副作用破壞 → todo 1 基線先行,todo 9/13 byte-compare 為硬 gate。

## Open Questions

- 無(規劃階段所有 fork 已於 approval gate 解決;審查缺陷已修正計畫)。
