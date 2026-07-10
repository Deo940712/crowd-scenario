# DONE — part-012: SOFTWARE_MIGRATION pack (2 slices)

Source: Codex review「更多 domain pack」+ 內部評估：第三個 domain 要證明引擎不是
「換皮的股票模型」。選 software migration / breaking-change rollout（非金融、非消費）。

## slice-001: SOFTWARE_MIGRATION pack + semantic sanity — DONE

- `src/crowdscenario/domains/software.py`：完整 pack——8 ecosystem cohorts
  (early_adopter / oss_maintainer / enterprise_ops / plugin_ecosystem / security_team /
  hobby_user / tech_influencer / conservative_team) × 3 axes
  (breaking_severity / migration_effort / value_gain)，顯示詞 **resist / wait / adopt**，
  2 個 persona variants（tech_influencer + hobby_user）。
- 匯出：`src/crowdscenario/__init__.py`（import + __all__）。
- `tests/test_engine.py`：`_PACKS` 加第三 pack（自動獲得決定論/categorical/no-leak/roster
  全套）；`test_software_pack_semantic_sanity_resist/adopt`；`test_software_pack_display_vocabulary`。

## slice-002: CLI + docs wiring — DONE

- `cli.py`：import + `_DOMAINS` 註冊 `software_migration` + `_FIXTURES`
  (big_rewrite / smooth_major / risky_major) + `_FALLBACK` 中性值。
- `tests/test_cli.py`：`test_run_software_migration_domain` + `test_run_software_migration_sweep`。
- README.md + README.zh-TW.md：domain 清單加第三 pack + CLI 範例。

## Semantic sanity (measured, not guessed)

| 情境 | buckets | consensus | display | net |
| --- | --- | --- | --- | --- |
| big_rewrite | rewrite / painful / negligible | negative | **resist** | -8 |
| smooth_major | minor / automated / substantial | positive | **adopt** | +8 |

方向由 pack 的 sensitivity/tilt 自然產生（非硬編），證明 DomainPack 協議承載得了與金融
完全不同的語義。

## Verification evidence

- `pytest -q` → **258 passed**（+新 pack 參數化 + 語義自檢 + CLI 冒煙）
- `ruff check .` → clean
- CLI: `run --domain software_migration --symbol big_rewrite --scenario v9_rewrite`
  → domain=software_migration, consensus=negative, display=resist
- CJK: software.py + 兩份 README → no mojibake

## Non-goals honored

- 未改引擎 core / DomainPack 協議（pack 直接塞進現有協議）。
- fixture 用抽象名（big_rewrite / smooth_major / risky_major），不影射真實專案。

## Incidents

None. (語義自檢的 resist/adopt 值全用實測捕捉，設計即正確，無需調參。)
