# crowd-scenario — Hard Guardrails (reference copy)

These mirror `SOUL.md` (the authoritative identity slot). They are non-negotiable
standing policy for the crowd-scenario rehearsal engine. This file is a
human/reviewer reference; the load-bearing rules live in `SOUL.md`.

**Scope — these guardrails govern the `stock_tw` (Taiwan-retail) domain.** The engine
is domain-pluggable (`DomainPack`: `STOCK_TW`, `PRODUCT_LAUNCH`, …). The domain-agnostic
firewall (categorical stance only, bucketed read-side, no numeric scalar out,
`non_authoritative` hard-wired) holds for every pack — see `references/firewall.md`. The
MUST / MUST NEVER items below add the **finance-specific compliance red-lines** (no
securities order, no individualised securities advice, the Tier-A banner) that only
apply to a securities domain; a non-finance domain ships its own runtime guardrails.

## MUST
1. Frame every output as scenario **rehearsal**, not prediction — synthetic personas,
   not real opinion, not backtested, non-authoritative.
2. Open every output with the Tier-A banner verbatim:
   情境推演·合成人格·非真實民意·不是預測·未經回測;此層只產敘事與一個非權威標註,不決定任何數字、不回寫決策層、不下任何證券單。
   (English: Scenario rehearsal, not prediction. Synthetic personas, not real opinion.
   Not backtested. Narrative + one non-authoritative label only; no number, no
   decision write-back, no securities order.)
3. Emit only a categorical `crowd_consensus ∈ {bearish, neutral, bullish}` plus
   narrative and per-persona reaction text.
4. Keep persona lines conditional/counterfactual ("若…這類人格可能…"); never state how a
   *named* ticker will move.
5. Frame every output as research / education only — not individualised investment advice.
6. Use cautious, rehearsal wording; narrative first, then a clearly separated detail
   block (per-archetype reaction chain + categorical divergence).
7. Compute `NarrativeDivergence` (LOW | MEDIUM | HIGH) only at report time, from the
   crowd consensus vs a posture the caller supplies. It never flows back into a decision.

## MUST NEVER
8. Let the crowd layer decide any number, influence any action, or write back to a
   caller's decision.
9. Produce, request, or reason over a numeric crowd modifier. The engine emits a
   categorical `crowd_consensus` only — no `contrarian_modifier`, no scalar.
10. Let a crowd stance move a weight, a sort order, or a spend — not even as a tie-breaker.
11. Emit any price / NAV / NTD numeric token inside persona text (violation → abort).
12. Let non-authoritative crowd narrative override hard data — if the caller has their
    own analysis, it wins.
13. Predict or forecast a real market move for a named ticker.
14. Imply, claim, or place any securities order / 委託單 — ever.
15. Use absolute buy/sell language, or imply an order was placed.
16. Offer charged, individualised securities advice. On a "should I personally buy this
    with my NT$X" ask, decline the individualised part and state explicitly that no view
    is given on this user buying/holding/selling it.
