# part-015 DESIGN

Source: 使用者觀察「感覺還是在模擬股票」。實證診斷:引擎計算邏輯(stance/consensus/
chain)完全領域無關,金融味道全在**命名、預設值、文件**——`market_scenario_label` 參數名、
engine 寫死 `register="zh-TW"` 與中文強度詞、README 股票優先、docstring 只舉金融例。
規劃與審查記錄:`.omo/plans/definance-crowd-scenario.md`。

## Goal

去金融化(de-finance):改命名/預設/文件,**行為與 emitted 輸出零變動**(byte-identical):

1. `make_seed` 改用 `scenario_label`(新名優先);`market_scenario_label` 保留為
   deprecated keyword-only alias(warn),兩者衝突拋 TypeError。
2. `register` 與 intensity 顯示詞移到 `DomainPack`(可覆寫欄位);三個現有 pack 不填
   → 預設沿舊值(`"zh-TW"`、溫和/劇烈)。
3. 兩份 README 主範例改 software_migration 領先,股票退為其一。
4. shared-core docstring 金融舉例中性化。

## Non-goals

- 不改 `ScenarioSeed.market_scenario_label` **欄位名**(序列化 schema break)。
- 不改 consensus 邏輯、persona 名冊、stance 數學、任何 emitted schema 欄位。
- 不改三個 pack 的實際輸出字串。不新增依賴。不用 `assert`。不 push(除非明示)。

## Assumptions(已實證)

- `make_seed` 40+ 呼叫點:第 3 參數(label)全位置傳遞、其餘全 keyword → 簽名演進
  只能把**新 alias** 設 keyword-only,其他參數位置不動。
- pyproject.toml 無 filterwarnings → DeprecationWarning 在 pytest 下可用 `pytest.warns` 測。
- `intensity_zh` 會進 `narrative_md`(deterministic.py:21)→ 預設詞必須是原字串,
  否則破決定論。`register` 不在 CLI JSON,但在 Python API `persona_samples[i].register`。
- 同 label 字串 → 同 seed hash(seed.py:51 json.dumps)→ C1 不影響決定論。

## Chosen Design

TDD、四 slices。簽名(審查後定稿):

```python
make_seed(symbol, metrics, scenario_label=None, rng_seed=42,
          horizon="swing", intensity="mild", pack=STOCK_TW,
          *, market_scenario_label=None)
```

DomainPack 新增 `register: str = "zh-TW"`、`intensity_display: Mapping[str, str]`
(default {"mild": "溫和", "severe": "劇烈"}),validate + deep-freeze 比照 part-014。
engine.py:241 改 `pack.register`、:261 改 `pack.intensity_display.get(seed.intensity, ...)`。

## Verification Targets

- `pytest -q` 全綠;`ruff` clean;LSP src/ = 0;`python -O` 契約綠。
- **硬 gate**:C1 後與 C2 後,三 domain `run` 輸出 byte-identical 於
  `.omo/evidence/baseline-*.json`(part-014 基線)。任何 diff → incident。

## Unit Test Strategy

- seed:新名可用;舊名可用且 warn;兩者不同值拋 TypeError;同值允許;皆缺拋 TypeError。
- pack:預設值正確;可覆寫;非字串 register/intensity_display 拒絕;凍結後不可變。
- engine:override pack 產生 `register="en"` 樣本與自訂強度詞敘事;預設 pack 輸出不變。

## Manual QA Strategy

- 新 shell 跑新舊參數路徑、override pack、三 domain byte-compare。

## Risks

- intensity 詞漂移破決定論 → 預設值用原字串常數,byte-compare 為 slice gate。
- 外部呼叫者位置傳參 → 簽名已對 40+ 呼叫點驗證,只有新 alias keyword-only。

## Open Questions

無(兩個 owner-decision 已由使用者拍板:保留 alias/新名優先;pack 覆寫/預設沿舊)。
