# DONE — part-009 / slice-003: Two-layer security claim in docs

## Goal (achieved)

把防火牆宣稱改為兩層表述（結構契約為主、掃描器為 defense-in-depth），誠實列出
T4/T5 限制，並修 backlog-006（「沒有任何數字離開引擎」過強宣稱）。

## What shipped

- `references/firewall.md`：新增「Two layers: structural contract vs. text scanner」
  段 + 掃描器威脅模型表（T1–T7，標明 T4/T5 為 known limitation）。
- `README.md`：
  - ASCII 圖 `no number ever leaves` → `no decision-grade scalar leaves` + 精確宣稱說明
    （bounded categorical integers 存在但非決策權重）。
  - 「Why firewalled」改兩層結構（Layer 1 結構契約 / Layer 2 文字掃描器）。
  - 賣點 bullet（firewall / LLM）、fusion firewall 段精確化 + 對抗覆蓋 + 限制。
  - layout 加 `firewall_corpus/`。
- `README.zh-TW.md`：對應中文全部同步（標題宣稱、ASCII 圖、賣點、fusion 段、layout）。

## backlog-006 resolved

「沒有任何數字/no number leaves」全部改為「無決策等級的可加總純量 + 無原始市場數字」，
並明確說明 `stance ∈ {-1,0,1}` / `narrative_intensity ∈ {1,2,3}` 是類別標籤非分數。

## Verification evidence

- CJK 編碼檢查：README.md / README.zh-TW.md / firewall.md 無 replacement char。
- `pytest -q` → **217 passed**（純文件改動，零影響）。
- `ruff check .` → clean。
- Manual QA: 文件宣稱與 corpus 實測一致（T1-T3/T6 攔、T4/T5 誠實標限制）。

## Incidents

None.
