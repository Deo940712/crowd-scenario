# crowd-scenario（群眾情境排練引擎）

> 一個**決定性**、**防火牆隔離**、**領域可插拔**的引擎，用來*排練*一群合成群眾對「已經
> 發生的事件」會有什麼反應——而且在架構上**無法把任何決策等級的純量回滲進你的決策**。

English → [README.md](README.md)

## 這個引擎在做什麼

你已經做了一個決定（升息落地了、漲價方案要上線了）。你想**排練**一下群眾可能怎麼反應
——不是預測未來，而是拿一個「合成的第二意見」來壓力測試你自己的判讀。

`crowd-scenario` 接收一個「分桶後的情境快照」，然後讓一群**人格原型（persona）**上場——
每個原型有自己的語氣、自己的敏感度——對這個事件做出反應。引擎把他們排成一條
**「誰先動」的反應鏈**（跟風快的先恐慌，看基本面的慢慢等），最後只吐出**一個類別性立場**
（`負面 | 中性 | 正面`）加上一段可讀的敘事。

就這樣。它**不決定任何數字、不建議任何動作、也絕不回寫進你的模型**。它是一盞**警示燈**，
不是方向盤。

```text
     你的情境                    引擎                        產出
 ┌────────────────┐   分桶     ┌──────────────────────┐    ┌───────────────────┐
 │ 折溢價 -0.6    │──────────▶│ 10 個人格各自反應,   │───▶│ 立場：偏多        │
 │ 殖利率  8.5    │ (數字在此 │ 排成「誰先動」的     │    │ + 反應鏈敘事      │
 │ 事件：降息     │  被丟棄)  │ 反應鏈,全程決定性    │    │                   │
 └────────────────┘           └──────────────────────┘    └───────────────────┘
       原始數字到此為止 ↑                      沒有任何決策等級純量離開 ↑
```

> **精確的宣稱。**「沒有數字離開」是簡稱。契約真正保證的是：**沒有決策等級的可加總
> 純量**（score / weight / modifier / 預期報酬）、**沒有原始市場數字**（價格 / 殖利率 /
> 淨值）出現在產出物上。有限的類別性整數*確實*會出現——人格 `stance ∈ {-1,0,1}`、
> `narrative_intensity ∈ {1,2,3}`、序號列表——但它們是固定有限集合的標籤，不是任何東西
> 能加總進決策的數值。

## 厲害在哪裡

- **防火牆本身就是產品，而且是靠架構、不是靠自律。** 引擎*無法*洩漏任何決策等級的
  純量，連不小心都做不到：原始指標在入口就被丟掉（讀取側的 `ScenarioSeed` 只收
  `"deep_discount"` 這類序數字串桶——原始數字連「建構成種子」都做不到），而它唯一能吐的
  東西是一個類別性標籤——輸出物件上**根本沒有任何可加總的浮點欄位**可以讓「就加個 0.05」
  這種洩漏藏身。契約用顯式 `ContractError` 檢查強制執行，連 `python -O` 都拔不掉。
  （另有文字掃描器為選配 LLM 敘事提供縱深防禦；結構性契約才是承重的保證。）
- **決定性、可重現。** 相同輸入 → 位元組完全相同的輸出，永遠如此。無網路、無時鐘、
  除了雜湊種子外沒有任何隨機。你可以 diff 兩次執行、在測試裡釘死它，並信任每次排練
  都可重複。
- **領域可插拔。** 引擎核心對「股票」一無所知。一個 `DomainPack` 提供人格、軸線、標籤
  ——所以*同一個*防火牆引擎既能排練台灣散戶（`STOCK_TW`）、產品發表
  （`PRODUCT_LAUNCH`）、軟體遷移（`SOFTWARE_MIGRATION`），或任何你能建模的群眾。壞掉的
  pack 甚至建構不出來——而且通過驗證後會被深度凍結，所以事後也無法被改壞成非法狀態。
- **允許 LLM，但絕不讓它作主。** 類別性決策是引擎在任何語言模型跑之前就做好的。選配的
  `FusionNarrator`（2 個 writer + 1 個 judge）可以把敘事寫得更漂亮，但每個模型輸出都
  會被決定性掃描器過濾，而且**不管有沒有跑 LLM，吐出的立場完全相同**。決策等級的
  部分（純量）從來不在模型手上——這個保證是結構性的，不靠掃描器。
- **零執行期依賴。** 純標準函式庫。放進任何專案都不會拖進一堆相依套件。

> **這是情境排練，不是預測。** 合成人格，不是真實民意；未經回測。這一層只產敘事——
> 不決定任何數字、不影響任何動作、也絕不回寫進決策。

## 運作原理（一句話）

`make_seed`（原始指標 → 分桶、雜湊過的種子）→ `run_scenario`（人格各自表態，排成反應鏈）
→ `CrowdNarrative`（一個類別性立場 + 敘事）。選配的 `compose_divergence` 還能把群眾
和*你自己*的判讀做對比。

## 安裝

```bash
pip install -e ".[dev]"      # 可編輯安裝 + 開發工具（pytest, ruff, hypothesis）
```

零執行期依賴——純標準函式庫。

## 從命令列使用

```bash
# 一次排練，股票領域（決定性；輸出 JSON）——--domain 預設是 stock_tw
python -m crowdscenario run --symbol 0056 --scenario 0056_cut

# 用時間尺度 + 衝擊強度重塑「誰先動」
python -m crowdscenario run --symbol 0056 --scenario 升息 --horizon long --intensity severe

# 換個領域：排練一次產品發表
python -m crowdscenario run --domain product_launch --symbol big_feature --scenario big_feature

# 讓群眾「方向」跟隨人格多數決，而不是種子雜湊擲骰
python -m crowdscenario run --domain product_launch --symbol price_hike --scenario price_hike --consensus-mode aggregate

# 餵你自己的原始指標（JSON），而不是內建的示範資料——只有它們的序數桶
# 會進到種子，原始數字絕不跨過防火牆
python -m crowdscenario run --symbol MYETF --scenario evt --metrics '{"discount_premium": -0.6, "yield": 8.5}'

# 一次跑 3 時間尺度 × 2 強度 的對照表
python -m crowdscenario run --symbol 0056 --scenario evt --sweep

# 決定性檢查——比對完整產物（立場 + 敘事 + 人格樣本 + seed_id）
python -m crowdscenario verify --symbol 0056 --scenario 0056_cut
```

各旗標：
- `--domain {stock_tw,product_launch,software_migration}`：選人格／軸線 pack。
- `--horizon {intraday,swing,long}`：改變「誰先動」（intraday → 最快的跟風者先動；
  long → 慢、低跟風的族群先動；swing → 名冊順序的中間態）。
- `--intensity {mild,severe}`：severe 會把反應鏈拉長、放大尾端。
- `--consensus-mode {hashed,aggregate,aggregate_neutral}`：決定群眾**方向**怎麼定——
  `aggregate_neutral`（**0.2.0 起的預設**：人格多數決、以中性為基線，方向跟隨情境而
  永不跟隨雜湊）、`hashed`（種子推導，0.2.0 前的行為）、或 `aggregate`（人格多數決但以
  雜湊為基線）。三者都是決定性、無數字純量。
- `--metrics '<json>'`：餵你自己的原始指標；未知 symbol 又沒給 `--metrics` 時會退回
  中性輸入並在 stderr 出警告。
- `--sweep`：一次輸出 6 格情境對照（會忽略 `--horizon/--intensity`）。

## 從 Python 使用

```python
from crowdscenario import make_seed, run_scenario, compose_divergence, posture_from_score
from crowdscenario import STOCK_TW, PRODUCT_LAUNCH

# --- 股票領域（預設 pack）---
seed = make_seed(
    "0056",
    {"discount_premium": -0.6, "yield": 8.5},   # 原始指標——只有它們的桶會存活
    market_scenario_label="0056_cut",
    horizon="long",
    intensity="severe",
    pack=STOCK_TW,
)
narrative = run_scenario(seed, pack=STOCK_TW)     # 決定性的 CrowdNarrative
print(narrative.crowd_consensus)                  # 'negative' | 'neutral' | 'positive'
print(STOCK_TW.consensus_display[narrative.crowd_consensus])  # 'bearish'|'neutral'|'bullish'
print(narrative.narrative_md)                     # 反應鏈故事

# --- 換個領域：同一引擎、不同 pack ---
seed = make_seed(
    "big_feature",
    {"price_change": 0.0, "value_delta": 0.7, "switching_cost": 0.5},
    market_scenario_label="big_feature",
    pack=PRODUCT_LAUNCH,
)
print(run_scenario(seed, pack=PRODUCT_LAUNCH).crowd_consensus)

# 把合成群眾和「你自己」的判讀做對比（你提供你的立場；引擎永遠看不到它）：
divergence = compose_divergence(narrative, posture_from_score(0.42))
print(divergence.divergence_bucket)               # 'LOW' | 'MEDIUM' | 'HIGH'
print(divergence.storylines)                      # 條件式的反事實劇本（無數字）
```

## 餵真實資料

防火牆的存在，正是為了讓你*可以*安全地把真實的決策等級數字餵進來——你爬到的情緒分數、
即時的折溢價、近四季殖利率——而它們不會外洩出去。`make_seed` 把每個原始指標分桶成序數
標籤、然後**把數字丟掉**，所以人格永遠只看到 `"deep_discount"`，看不到 `-1.5`。

模式是依賴注入：你提供一個 `fetch_metrics(symbol) -> dict`（你的爬蟲／API／DB），引擎做
其餘的事。可執行、離線的範例在 [`examples/real_data.py`](examples/real_data.py)：

```python
def fetch_metrics(symbol):        # <- 你的真實資料層放這裡
    return {"discount_premium": -0.6, "yield": 8.5}

raw = fetch_metrics("0056")       # 真實數字只活在這個區域變數裡……
seed = make_seed("0056", raw, market_scenario_label="rate_cut", pack=STOCK_TW)
# ……到這裡就沒了：種子帶的是桶，不是數字。
print(run_scenario(seed, consensus_mode="aggregate").crowd_consensus)
```

## 案例研究（Case studies）

三份可重現、離線的案例研究，展示引擎「哪裡有用、哪裡不能信」——見
[`case_studies/`](case_studies/README.md)：

- **[CASE A](case_studies/case_a_etf_discount.md)**：ETF 深折價＋高殖利率（stock_tw）——
  群眾偏 `positive`，由基本面派帶頭。
- **[CASE B](case_studies/case_b_price_hike.md)**：漲價但價值提升不足（product_launch）——
  八種 cohort 一致反對；同時是 0.2.0 改 default 的活教材（舊 `hashed` 擲出 `neutral`，
  新 default 正確給 `negative`）。
- **[CASE C](case_studies/case_c_premium_chase.md)**：溢價＋低殖利率追高（stock_tw）——
  群眾對 FOMO 追高潑冷水（你偏多 → HIGH divergence）。

每份都以必填的**「哪裡不能信」**段作結——這是排練，不是預測。

## 領域與人格

一個 `DomainPack` 是把人格名冊、N 條序數軸（各自帶分桶函式 + 傾向表）、每人格的敏感度、
以及「中性 → 顯示標籤」對照，**深度凍結**成一個 bundle。`validate_pack` 在建構時就跑，
之後所有 mapping 都唯讀，所以非法 pack 既建不出來、也改不壞（含非 finite 權重、
voice-variant stance key 越界都會被拒）。內建三個 pack：

- **`STOCK_TW`** — 10 個台灣散戶原型，兩條軸（`discount_premium`、`yield`）：
  存股族 / 當沖客 / 殖利率派 / 槓桿 ETF 玩家 / 外資視角 / 恐慌散戶 /
  PTT·Dcard 風向 / 媽媽存股社團 / 主力·中實戶 / 定期定額新手。
- **`PRODUCT_LAUNCH`** — 8 個使用者族群，三條軸（`price_change`、`value_delta`、
  `switching_cost`）：嘗鮮玩家 / 免費用戶 / 重度用戶 / 精打細算族 / 品牌鐵粉 /
  競品愛好者 / 輕度用戶 / 社群風向。
- **`SOFTWARE_MIGRATION`** — 8 個生態系族群，三條軸（`breaking_severity`、
  `migration_effort`、`value_gain`），顯示詞為 `resist / wait / adopt`：嘗鮮開發者 /
  下游套件維護者 / 企業運維 / 外掛生態作者 / 資安團隊 / 業餘使用者 / 技術風向 KOL /
  保守團隊。既非金融、也非消費產品——這是引擎領域無關性最清楚的證明。試試：
  `run --domain software_migration --symbol big_rewrite --scenario v9_rewrite`。

每個人格有自己的語氣、對序數情境有自己的敏感度，所以在同一情境裡他們會彼此分歧，而不是
整齊劃一地一起翻面。要新增領域，就建一個 `DomainPack`（參考
`src/crowdscenario/domains/product.py`）並傳給 `make_seed`／`run_scenario`。

## 敘事這一層（選配的 LLM）

**類別性決策永遠是引擎做的**——決定性且防火牆隔離——*在*任何 narrator 跑之前就決定好了。
一個 **narrator** 只把這些既定事實變成散文，它永遠改不了立場、共識，也帶不進數字。

- **`DeterministicNarrator`**（預設）——離線、純標準庫、查表式散文。相同事實 → 位元組
  完全相同的敘事。不傳任何東西時 `run_scenario` 就用它。
- **`FusionNarrator`** — **2 個 writer 模型 + 1 個 judge 模型**。writer 各自對既定事實
  草擬敘事；一個規則式防火牆掃描器過濾**每一個**模型輸出（包含 writer *和* judge）；
  judge 挑選／融合存活者。若沒有任何乾淨版本存活——或模型出錯——就**退回決定性
  narrator**。

模型以純 `str -> str` callable 注入，所以核心維持零依賴、整套可離線測試。不論你用哪個
narrator，`run_scenario` 吐出的 `crowd_consensus` 和 `persona_samples` 都一樣——只有散文
會變。

**融合路徑的防火牆保證。** 任何模型輸出只要含有數字市場 token（價格 / 淨值 / 台幣 / % /
殖利率，半形*或*全形數字、中文數字＋單位都算）、內部訊號編碼（`stance=` / `score=` /
`modifier=` / `weight=`）、下單語（買進／賣出／委託單 …）、或 prompt-injection 標記詞
（忽略前述… / ignore previous…），都會被**拒絕、而非清洗**——掃描器
（`crowdscenario.scan_violations`）在比對前先做 NFKC 正規化與去空白，所以拆字偽裝
（`買 進`、`Ｂ Ｕ Ｙ`）會先塌回原形。它決定性且離線，並由對抗性 corpus
（`tests/test_firewall_adversarial.py`）驗證。融合 prompt 把人格立場以文字給
（偏空／中性／偏多），從不給裸的 `-1/0/+1`。任何洩漏就代表那個候選被丟棄；安全的決定性
散文永遠是保底。

這個掃描器是**縱深防禦，不是語義安全證明**：沒有禁詞的純語義建議、以及編碼／混淆的
內容，是它攔不住的**已知限制**——這可以接受，因為*結構性*契約（無純量欄位、無原始輸入）
無論如何都成立。融合路徑本身不可重現（LLM 會漂移），但吐出的 `crowd_consensus` **是**
可重現的——它永遠不來自模型。（完整威脅模型見 `references/firewall.md`。）

## 專案結構

```
src/crowdscenario/
  contracts.py       ScenarioSeed / CrowdNarrative / PersonaReaction / NarrativeDivergence
  domains/
    base.py          DomainPack / Axis / validate_pack — 可插拔領域協議
    stock_tw.py      STOCK_TW — 10 個台灣散戶原型（2 軸）
    product.py       PRODUCT_LAUNCH — 8 族群的產品發表領域（3 軸）
    software.py      SOFTWARE_MIGRATION — 8 族群的軟體遷移領域（3 軸）
  narrator/
    base.py          NarratorBackend / EngineFacts — 唯讀事實交接
    firewall.py      scan_violations — 每個 LLM 輸出都要過的規則式掃描（縱深防禦）
    deterministic.py DeterministicNarrator — 預設離線查表散文
    fusion.py        FusionNarrator — 2 writer + 1 judge，全程防火牆過濾
  seed.py            make_seed — 原始指標 → 分桶、雜湊的 ScenarioSeed
  engine.py          run_scenario — 讀 pack + narrator：立場邏輯 + 反應鏈
  composer.py        compose_divergence — 群眾 vs 你自己的判讀（報告時）
  cli.py             python -m crowdscenario run | verify
examples/            real_data.py — 安全接真實資料的可執行範例
references/          personas.md（名冊）、firewall.md（契約）
tests/               契約 + 引擎 + narrator/fusion + property-based（離線）
```

## 視覺報告

把一次 `--sweep` 變成單檔 self-contained HTML 報告——3×2 的 horizon×intensity 網格、
persona 分布以顏色類別呈現（**不畫數字條**——防火牆延伸到視覺層）、以及固定的
「排練非預測」免責。決定性、XSS-safe（所有動態文字都經 HTML-escape）。

```bash
# 把 sweep 餵給報告產生器（repo 根要在 path 上）
#   PowerShell:  $env:PYTHONPATH="src;$PWD"
#   bash:        export PYTHONPATH="src:$PWD"
python -m crowdscenario run --symbol 0056 --scenario evt --sweep | \
    python tools/report.py --out report.html
```

`tools/report.py` 純標準庫、只留在 repo（不進 wheel）。

## 測試

```bash
pytest -q          # 引擎 + 防火牆契約 + narrator/fusion + property-based 不變量
ruff check .       # lint
```

測試同時涵蓋範例式測試*和* hypothesis property 測試（決定性、輸出恆為類別性、無原始
數字外洩、單調性）。防火牆契約在 CI 裡另外用 `python -O` 斷言，所以最佳化模式永遠拔不掉。

## 授權

MIT。
