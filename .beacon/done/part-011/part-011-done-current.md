# DONE — part-011: Static HTML comparison report

Source: Codex review「漂亮的 comparison UI」+ 內部評估第四優先「展示」。

## slice-001: HTML report generator — DONE

- `tools/report.py`：stdlib-only 靜態 HTML 產生器。吃 `run --sweep` JSON →
  單檔 self-contained HTML：3×2 horizon×intensity 網格 + persona 分布（**顏色類別，
  非數字條**——視覺層防火牆）+ 固定「排練非預測」免責。
  - 決定性（同 JSON 同 HTML）。
  - **XSS-safe**：所有動態文字（domain/seed_id/consensus_mode）HTML-escaped。
  - inline CSS、無模板引擎、無 CDN、無 JS 依賴。
  - stdin 或 `--input`；stdout 或 `--out`。
- `tests/test_report.py`：決定論 / 6 格齊全 / 免責存在 + 無 raw 數字 / hostile symbol
  XSS-escape（hostile `--symbol` 流入 seed_id → 驗證被 escape）。

## slice-002: README showcase — DONE

- README.md + README.zh-TW.md：Visual report / 視覺報告 小節（一句話 + 產生指令）。

## Non-goals honored

- 無 runtime 依賴進引擎 core（report.py 在 tools/，不進 wheel）。
- 無數字分數條（視覺層防火牆）。
- 無聊天介面。

## Verification evidence

- `pytest -q` → **262 passed**（+4 report tests）
- `ruff check .` → clean
- Manual QA: `run --domain software_migration ... --sweep | report.py --out rep.html`
  → 2760 bytes HTML，含 disclaimer + resist。
- CJK: report.py + 兩份 README → no mojibake。

## Incidents

None. (XSS 測試原針對 scenario label，但該欄位未進報告；改針對 hostile symbol
——它經 seed_id 進報告——是更真實的攻擊面。)
