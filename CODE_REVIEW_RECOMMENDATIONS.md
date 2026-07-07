# Code Review 改進建議

這份文件整理目前最值得優先處理的改進項目。重點不是單純整理程式風格，而是讓這個專案的核心定位更穩：一個 deterministic、firewalled、domain-pluggable 的 crowd scenario rehearsal engine。

目前狀態：

- `pytest -q` 通過：48 tests passed
- `ruff check .` 通過
- 主要風險集中在 contract enforcement、domain/seed mismatch、domain pack validation、LLM narrator 可觀測性

## 優先順序總覽

| Priority | Area | 建議 |
| --- | --- | --- |
| P1 | Contract safety | 不要用 `assert` 當正式 runtime contract |
| P1 | Seed/domain integrity | `ScenarioSeed` 應記住產生它的 `domain_id`，並由 `run_scenario` 檢查 pack 是否一致 |
| P2 | Domain validation | 缺 metric 或未知 bucket 應 fail-fast |
| P2 | Fusion narrator firewall | 避免把 `stance=-1/0/+1` 這種數字訊號交給或輸出自 LLM |
| P3 | Observability | `CrowdNarrative` 應保留 narrator backend / notes |
| P3 | CLI usefulness | `verify` 應驗完整 artifact，並支援 horizon / intensity |

## P1: 用明確例外取代 `assert`

### 問題

目前 `contracts.py` 和 `domains/base.py` 用 `assert` 做關鍵契約檢查，例如：

- `crowd_consensus` 必須在 vocabulary 裡
- `n_personas` 必須是 0 或 20..50
- `non_authoritative` 必須固定為 `True`
- `DomainPack` 的 persona parallel tables 必須對齊

但 Python 在 `python -O` optimize mode 下會移除 `assert`，這會讓 firewall contract 失效。

### 建議

改成顯式檢查：

```python
if self.crowd_consensus not in CONSENSUS:
    raise ValueError("crowd_consensus out of vocabulary")
```

或建立專用例外：

```python
class ContractError(ValueError):
    pass
```

### 驗收標準

- `python -O` 下仍然會拒絕非法 contract
- 測試改成檢查 `ValueError` 或 `ContractError`
- `tests/test_contracts.py` 加一個 optimize-mode 不會繞過 contract 的測試，或至少把 assert-based expectation 全部替換掉

## P1: 讓 `ScenarioSeed` 綁定 domain

### 問題

`make_seed` 有把 `pack.domain_id` 放進 hash，但 `ScenarioSeed` 本身沒有保存 `domain_id`。因此呼叫端可能不小心用 stock seed 去跑 product pack：

```python
seed = make_seed("x", stock_metrics, "evt", pack=STOCK_TW)
run_scenario(seed, pack=PRODUCT_LAUNCH)
```

目前這種錯配不會報錯，會產生看似正常但語義錯位的 narrative。

### 建議

在 `ScenarioSeed` 增加欄位：

```python
domain_id: str
```

在 `make_seed` 回傳時填入：

```python
domain_id=pack.domain_id
```

在 `run_scenario` 開頭檢查：

```python
if seed.domain_id != pack.domain_id:
    raise ValueError("seed domain does not match pack domain")
```

可選擴充：

- `axis_names: tuple[str, ...]`
- `pack_version: str`

這樣未來 domain pack 更新時，也能判斷 seed 是否由相容的 pack 建立。

### 驗收標準

- stock seed + stock pack 正常
- product seed + product pack 正常
- stock seed + product pack 會報錯
- 新增測試覆蓋錯配情境

## P2: 缺 metric 或未知 bucket 應 fail-fast

### 問題

目前 `make_seed` 會用：

```python
metrics.get(axis.name, 0.0)
```

如果呼叫端拼錯 metric name，會默默使用 `0.0`。

`engine._stance_for` 也會用：

```python
axis.tilt.get(bucket, 0.0)
```

如果 bucket function 回傳了 `axis.tilt` 裡不存在的 bucket，會默默當成中性。

這對 domain-pluggable 設計很危險，因為新增 domain 時 typo 很難被發現。

### 建議

預設改成 fail-fast：

```python
if axis.name not in metrics:
    raise ValueError(f"missing metric for axis {axis.name!r}")
```

以及：

```python
if bucket not in axis.tilt:
    raise ValueError(f"unknown bucket {bucket!r} for axis {axis.name!r}")
```

若 CLI 需要 demo fallback，可以只在 CLI 層處理 fallback，不要讓 library API 預設吞錯。

### 驗收標準

- metric 缺漏會報錯
- bucket typo 會報錯
- CLI fixture fallback 仍可正常跑
- 測試覆蓋 missing metric / unknown bucket

## P2: Fusion narrator 不應使用數字 stance

### 問題

`FusionNarrator` 的 prompt 會傳：

```text
stance=-1
stance=0
stance=1
```

目前 firewall scanner 不會擋 `stance=-1`。如果 LLM 照抄 prompt，最後 narrative 可能含有數字訊號。雖然這不是 market price/yield，但仍削弱「輸出不應帶可被誤用的數字訊號」這個產品精神。

### 建議

把 prompt 中的 stance 改成文字：

```python
STANCE_LABELS = {
    -1: "opposes",
    0: "neutral",
    1: "supports",
}
```

或用 domain-neutral wording：

- `negative`
- `neutral`
- `positive`

另外可讓 scanner 擋：

- `stance=`
- `score=`
- `modifier=`
- `weight=`

### 驗收標準

- Fusion prompt 不再包含 `-1`、`0`、`+1` stance encoding
- LLM output 若包含 `stance=-1` 會被拒絕
- 現有 fusion fallback 測試仍通過

## P3: 保留 narrator provenance

### 問題

`NarratorResult` 已有：

- `backend`
- `notes`

但 `run_scenario` 只取：

```python
narrative = narrator.render(facts).narrative_md
```

所以最後 `CrowdNarrative` 不知道 narrative 是：

- deterministic
- fusion judge
- fusion writer fallback
- fusion deterministic fallback

實務上這會降低 debug 和 observability。

### 建議

在 `CrowdNarrative` 增加：

```python
narrator_backend: str = "deterministic"
narrator_notes: tuple[str, ...] = field(default_factory=tuple)
```

在 `run_scenario` 保留完整 result：

```python
narrator_result = narrator.render(facts)
```

CLI JSON 也輸出：

- `narrator_backend`
- `narrator_notes`

### 驗收標準

- deterministic path 顯示 `deterministic`
- fusion judge path 顯示 `fusion:judge`
- fusion fallback path 顯示 `fusion:fallback`
- CLI output 包含 narrator provenance

## P3: 強化 CLI `verify`

### 問題

目前 `verify` 只比較 `crowd_consensus`：

```python
a, b = once(), once()
ok = a == b
```

如果 narrative、persona order、persona samples 不穩，`verify` 仍可能顯示 OK。

另外 `verify` 目前沒有 `--horizon` / `--intensity`，但這兩個欄位會影響 seed 和 narrative。

### 建議

讓 `verify` 比較完整 artifact，例如：

- `crowd_consensus`
- `narrative_md`
- `persona_samples`
- `seed_id`

並補上：

```text
--horizon {intraday,swing,long}
--intensity {mild,severe}
```

### 驗收標準

- 完整 deterministic artifact 不一致時 `verify` 會 fail
- `verify --horizon long --intensity severe` 可正常執行
- README 的 CLI 範例同步更新

## 其他小改進

### 移除重複 bucket function

`seed.py` 和 `domains/stock_tw.py` 都有：

- `bucket_discount_premium`
- `bucket_yield`

既然現在 bucket function 已經在 `DomainPack.axes` 裡，`seed.py` 裡的 stock-specific bucket function 可以移除，避免未來兩邊不同步。

### 增加 domain pack 測試 helper

可以建立一個測試 helper，確保每個 pack 都通過：

- 每個 axis 的 bucket function 回傳值都存在於 `axis.tilt`
- 每個 voice 都完整覆蓋 `-1, 0, 1`
- display name 不為空字串
- horizon frame 覆蓋 `intraday, swing, long`

這會讓新增第三個 domain 時更安全。

## 建議實作順序

1. Contract hardening：把 `assert` 改成明確 exception
2. Seed/domain integrity：`ScenarioSeed.domain_id` + `run_scenario` mismatch check
3. Domain validation：missing metric / unknown bucket fail-fast
4. Narrator firewall：移除數字 stance，補 scanner 規則
5. Observability：把 narrator backend / notes 帶到 `CrowdNarrative` 和 CLI
6. CLI verify：驗完整 artifact，補 horizon / intensity
7. 清理重複 bucket function 和補 domain pack helper tests

## 建議測試清單

- `test_contracts_survive_python_optimized_mode`
- `test_run_scenario_rejects_seed_pack_domain_mismatch`
- `test_make_seed_rejects_missing_metric_by_default`
- `test_stance_rejects_unknown_axis_bucket`
- `test_fusion_prompt_uses_textual_stance_labels`
- `test_firewall_rejects_numeric_stance_tokens`
- `test_crowd_narrative_preserves_narrator_provenance`
- `test_cli_verify_compares_full_artifact`

## 指令

```bash
python -m pytest -q
python -m ruff check .
python -m crowdscenario run --domain stock_tw --symbol 0056 --scenario 0056_cut
python -m crowdscenario verify --domain stock_tw --symbol 0056 --scenario 0056_cut
```

