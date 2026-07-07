# HANDOFF — crowd-scenario 後續實作交接

> 給接手的 session：這份文件讓你**不必重讀整個對話**就能無縫接手。先讀完本檔，
> 再讀 `AGENTS.md`（防火牆紅線）與 `README.md`（產品定位），然後動工。所有指令在
> Windows PowerShell 5.1 下驗證過；CLI 需要 `$env:PYTHONPATH='src'`。

---

## 0. 30 秒現況

- **這是什麼**：deterministic、firewalled、domain-pluggable 的「群眾情境**排練**器」
  （rehearsal，不是 forecast）。讀 bucketed `ScenarioSeed`，只吐 categorical
  `crowd_consensus ∈ {negative,neutral,positive}` + 敘事。**沒有任何數字純量能離開引擎。**
- **狀態**：綠燈。`pytest -q` → **62 passed**；`ruff check .` → clean；`python -O`
  contract 冒煙 → enforced。尚未 commit（branch `master`，no commits yet）。
- **剛完成**：一輪 code-review 硬化（12 項，見 §2）。**未動引擎的決定論行為**——
  deterministic 敘事仍 byte-stable。
- **要做**：2 個高價值可用性改進（見 §3），規格已定，可直接實作。

---

## 1. 架構地圖（檔案 → 職責）

```
src/crowdscenario/
  contracts.py       ScenarioSeed / CrowdNarrative / PersonaReaction /
                     NarrativeDivergence + ContractError + vocabulary tuples
  domains/
    base.py          DomainPack / Axis / validate_pack（可插拔協議 + 不變量）
    stock_tw.py      STOCK_TW（10 台股散戶原型，2 軸：discount_premium, yield）
    product.py       PRODUCT_LAUNCH（8 cohort，3 軸）
  narrator/
    base.py          NarratorBackend / EngineFacts / PersonaFact / NarratorResult
    firewall.py      scan_violations / is_clean（每個 LLM 輸出必過的規則掃描）
    deterministic.py DeterministicNarrator（預設離線 table-lookup prose）
    fusion.py        FusionNarrator（2 writer + 1 judge LLM，全程 firewall 過濾）
  seed.py            make_seed（raw metrics → bucketed hashed ScenarioSeed）
  engine.py          run_scenario（stance 邏輯 + who-moves-first 反應鏈）
  composer.py        compose_divergence（群眾 vs 你自己的 read，report time）
  cli.py             python -m crowdscenario run | verify
tests/
  test_contracts.py   契約 + DomainPack 不變量
  test_engine.py      引擎行為
  test_narrator.py    firewall + fusion（用 fake callables，離線）
  test_improvements.py 本輪硬化的回歸鎖（13 個函式，1 個參數化×2 → 14 測試項）
```

**資料流**：`make_seed`（seed.py）→ `run_scenario`（engine.py：`_internal_view` →
`_consensus` → per-persona `_stance_for` → `_reaction_chain` → narrator）→
`CrowdNarrative`。可選 `compose_divergence`（composer.py，report time，永不回寫）。

---

## 2. 已完成的硬化（DO NOT 回退這些）

本輪把 code-review 的 7 項 + 6 項補充全部實作。關鍵不變量，改動時**必須維持**：

1. **契約用 `raise ContractError`，永不用 `assert`** — assert 在 `python -O` 下會被
   移除，會讓防火牆失效。`contracts.py` 與 `domains/base.py::validate_pack` 皆已改。
   新增任何契約檢查都要遵守這條。
2. **seed 綁 domain** — `ScenarioSeed.domain_id` 由 `make_seed` 從 pack 填入；
   `run_scenario` 檢查 `seed.domain_id != pack.domain_id` 即 `raise ContractError`。
3. **`ordinal_context` 深凍結** — `__post_init__` 包成 `MappingProxyType`。frozen
   dataclass 只擋 rebind，擋不住 dict 內容竄改。
4. **fail-fast** — `make_seed` 缺 axis metric → raise（不再靜默 `0.0`）；
   `_stance_for` 遇到 `axis.tilt` 沒有的 bucket → raise（不再靜默中性）。CLI demo
   fallback 只在 `cli.py`，library API 不吞錯。
5. **掃描器強化** — 擋全形數字 `[０-９]`/全形 `％`、`stance=/score=/modifier=/weight=`、
   裸 `買進/賣出`。**注意**：`加碼/減碼/停損` 是合法 persona 語音（描述性條件語氣），
   **刻意不擋**——已驗證兩個 pack 的 voice 都無裸買賣。動掃描器前先跑
   `test_deterministic_narrative_is_clean`，別誤殺乾淨敘事。
6. **fusion prompt 用文字立場** — `_STANCE_LABEL = {-1:"偏空",0:"中性",1:"偏多"}`，
   不再把 `stance=-1` 這種數字編碼餵給 LLM。
7. **narrator provenance** — `CrowdNarrative.narrator_backend` / `narrator_notes`
   帶出，CLI JSON 也輸出。
8. **validate_pack 加強** — voice 必須覆蓋 `{-1,0,1}`、display_name 非空。
9. **CLI verify** — 比較完整 artifact（seed_id + consensus + narrative + samples），
   加 `--horizon/--intensity`。
10. **清理** — 刪 seed.py 重複 bucket fn、消除 `_stance_for` 雙重呼叫、加 `py.typed`。
11. **CI** — `.github/workflows/ci.yml`（pytest + ruff + `-O` 冒煙，3.10/3.12）。
12. **文件** — README/AGENTS.md 同步。

---

## 3. 待實作（規格已定，可直接做）

### ★ 任務 A（最高價值）：共識可回應情境語義

**問題**：`crowd_consensus` 的方向來自 `hashlib.sha256(seed.seed_hash)`
（`engine.py::_internal_view`，約 L37-40；行號以搜尋 `def _internal_view` 為準）→ 純骰子。`ordinal_context`（折價/殖利率
buckets）只影響**個別 persona 的 stance**，不影響**共識方向**。結果會出現「深度折價
+高殖利率、但共識偏空、而多數 persona 偏多」的自相矛盾敘事。這是「群眾分析」定位的
最大語義弱點。

**設計**（categorical、決定論、零防火牆風險）：
- 新增共識模式參數：`consensus_mode: Literal["hashed","aggregate"] = "hashed"`
  （預設 `hashed` = **維持現行為**，不破壞既有測試與決定論）。
- `aggregate` 模式：先算完所有 persona 的 stance（需要先有一個 baseline consensus
  餵給 `_stance_for` 當 seed lean），再**多數決聚合**成共識：
  - `sum(stance)` > 門檻 → positive，< -門檻 → negative，否則 neutral。
  - **tie-break 用 seed hash**（保持決定論），不要用 Python 內建順序。
- **雞生蛋問題**：`_stance_for` 目前吃 `consensus` 當 baseline lean。aggregate 模式
  下需先用 hashed consensus（或 neutral）當 baseline 算 stance，再聚合。要在 docstring
  講清楚這個兩階段，並確保**同 seed 必同結果**。
- 門檻設計：讓 aggregate 對「深折價+高息」這類明確情境**方向正確**（偏多），對中性
  情境維持 neutral。用參數化測試鎖 3-4 個代表情境。

**驗收**：
- `hashed` 模式所有既有測試與敘事 byte-identical（回歸零漂移）。
- `aggregate` 模式：深折價+高息 → consensus 與多數 persona stance **方向一致**。
- 同 seed 兩次 aggregate 結果完全相同（決定論）。
- 防火牆不變量全過（不得因此新增任何數字純量欄位）。
- 新測試檔或加進 `test_engine.py`：`test_aggregate_consensus_follows_personas`、
  `test_aggregate_consensus_is_deterministic`、`test_hashed_mode_unchanged`。

**觸及檔案**：`engine.py`（主要）、可能 `contracts.py`（若參數需上到 CLI/API）、
`cli.py`（加 `--consensus-mode`）、`__init__.py`（若導出新型別）。

---

### ★ 任務 B：CLI 可輸入自訂 metrics

**問題**：`cmd_run`/`cmd_verify` 只吃內建 `_FIXTURES`；symbol 無 fixture 就**靜默**用
`_FALLBACK` 中性值（`cli.py::_metrics_for` L55-56）。等於 **CLI 只能跑 demo**，真實
使用被迫寫 Python。而且這正是我們在 library 層剛修掉的「靜默吞錯」，CLI 層還留著。

**設計**：
- `run` 與 `verify` 都加 `--metrics '<json>'`（JSON 物件字串），例如
  `--metrics '{"discount_premium": -0.6, "yield": 8.5}'`。
- 優先序：`--metrics`（若給）> fixture（若 symbol 命中）> fallback。
- **fallback 時印 stderr 警告**（不要靜默），例如
  `warning: no fixture/metrics for '<symbol>', using neutral fallback`。
- `--metrics` JSON parse 失敗 → 友善錯誤訊息 + 非零退出，不要 traceback。
- library 的 `make_seed` 已對缺 metric fail-fast，所以 `--metrics` 給不全會自然
  報 `ContractError`——CLI 要 catch 成乾淨訊息。

**驗收**：
- `run --domain stock_tw --symbol XYZ --metrics '{"discount_premium":-0.6,"yield":8.5}'`
  正常輸出，且 consensus/敘事反映該輸入。
- 缺 metric 的 `--metrics` → 乾淨錯誤（非 traceback）、非零退出。
- 無 fixture 無 metrics → 印警告 + 仍用 fallback 跑完。
- 加 CLI 層測試（可用 `build_parser().parse_args` + `capsys`）。

**觸及檔案**：`cli.py`。

---

### 次要（時間夠再做，非阻塞）

- **`NarrativeDivergence.storylines` 是死欄位**：`compose_divergence` 從沒填它。要嘛
  實作（HIGH divergence 時產反事實敘事，很契合「排練」定位），要嘛刪。半成品欄位比
  沒有差。
- **`swing` 排序 = intraday 別名**：`_reaction_chain` 用 `reverse=bias >= 0`
  （engine.py 約 L107；搜尋 `reverse=bias` 定位），swing bias=0.0 → 與 intraday 同向。給 swing 明確的中間行為，
  用測試鎖三 horizon 排序確實不同。
- **敘事多樣性**：每 persona/stance 只有一句 canned voice → 同 stance 組合逐字相同。
  可每 stance 給 2-3 句變體，由 seed hash 選（仍 byte-stable）。
- **真實資料接入 worked example**：文件示範如何安全把真實輿情分數餵進 bucket 軸
  （原始分數在 make_seed 就死掉，防火牆本就支援，缺的只是範例）。
- `CrowdNarrative` 加 `schema_version`；`run --sweep`（一次跑 3×2 情境對照）；
  property-based 測試（hypothesis）；發佈 PyPI。

---

## 4. 防火牆紅線（動任何 code 前必讀）

摘自 `AGENTS.md`，違反即真 bug：

1. **無數字純量可離開引擎**。`CrowdNarrative`/`NarrativeDivergence` 不得有
   `modifier`/`score`/`weight`/任何 float。任務 A 的聚合**只產 categorical**。
2. **read-side 只有 bucket**。raw metric 在 `seed.py` 就丟掉，只有 ordinal bucket
   進 seed。
3. **契約自驗用 `raise ContractError`，不用 assert**（見 §2.1）。
4. persona 內部 stance `∈ {-1,0,+1}` 只是排序標籤，emission 前 threshold 回
   categorical。
5. 引擎保持 pure/offline：無網路、無時鐘、除 seed hash 外無隨機。

---

## 5. 驗證指令（每次改完都跑）

```powershell
# 測試 + lint
python -m pytest -q                         # 期望：全綠（目前 62）
python -m ruff check .                       # 期望：All checks passed

# python -O 契約冒煙（防火牆不可被 -O 繞過）
$env:PYTHONPATH='src'
python -O -c "from crowdscenario.contracts import CrowdNarrative, ContractError
try:
    CrowdNarrative(seed_id='x', rng_seed=1, n_personas=30, crowd_consensus='BAD', narrative_md='t')
except ContractError: print('O-mode OK')
else: print('O-mode FAIL')"

# CLI 冒煙（CLI 需要 PYTHONPATH=src）
$env:PYTHONPATH='src'
python -m crowdscenario run --symbol 0056 --scenario 0056_cut
python -m crowdscenario verify --symbol 0056 --scenario 0056_cut --horizon long --intensity severe
python -m crowdscenario run --domain product_launch --symbol big_feature --scenario big_feature

# 決定論回歸（改引擎後必驗 hashed 模式 byte-stable）
$env:PYTHONPATH='src'
python -c "from crowdscenario import make_seed, run_scenario, STOCK_TW
a=run_scenario(make_seed('0056',{'discount_premium':-0.6,'yield':8.5},'0056_cut',pack=STOCK_TW))
b=run_scenario(make_seed('0056',{'discount_premium':-0.6,'yield':8.5},'0056_cut',pack=STOCK_TW))
assert a.narrative_md==b.narrative_md and a.persona_samples==b.persona_samples
print('deterministic OK', a.crowd_consensus)"
```

---

## 6. 環境注意事項

- OS：win32 / PowerShell 5.1。鏈式指令用 `cmd1; if ($?) { cmd2 }`，**不要用 `&&`**。
- Python 3.12.4（本機）；專案 target py310，`requires-python >=3.10`。
- **零 runtime 依賴是刻意的**（`dependencies = []`）——**不要加任何 runtime dep**。
  dev 工具（pytest/ruff）在 `[project.optional-dependencies].dev`。
- `pyproject.toml` 設 `pythonpath=["src"]`，所以 **pytest 免裝可跑**；但 **`python -m
  crowdscenario` 需要 `$env:PYTHONPATH='src'`**（或先 `pip install -e .`）。
- Ruff 規則：`E,F,I,B,UP`，line-length 100。改完跑 `ruff check --fix .` 收 import 排序。

---

## 7. 建議動工順序

1. 讀本檔 + `AGENTS.md` + `README.md`（§0 已列）。
2. 跑 §5 全套，確認接手時是綠燈基線。
3. **任務 A**（共識聚合）— 影響力最大，先做。TDD：先寫 `test_hashed_mode_unchanged`
   鎖回歸，再加 aggregate 測試，最後實作。
4. **任務 B**（CLI --metrics）— 獨立、低風險。
5. 每步跑 §5，確認決定論與防火牆不變量不破。
6. 次要項目視時間。
