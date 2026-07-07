# Persona taxonomy — a closed roster per domain pack

Personas are not hard-coded in the engine any more. Each **`DomainPack`** carries its
own closed persona roster plus the parallel tables that describe them; the engine
reads whichever pack you pass in. The consensus label is seed-driven, so roster size
never moves a categorical outcome. Every persona has:

- a `herding` speed (orders the reaction chain — who moves first → who follows → who
  sits still),
- a membership in `contra_ids` or not (`contra` fades the consensus; the rest amplify),
- a `sensitivity` tuple — one weight per ordinal **axis** the pack defines (how much
  its own read of the context can override the baseline lean).

The two shipped packs are below. To add a domain, build a new `DomainPack` with the
same shape (see `src/crowdscenario/domains/product.py`); `validate_pack` enforces that
the parallel tables line up and the sensitivity tuples match the axis count.

## `STOCK_TW` — Taiwan retail (10 personas, 2 axes)

Axes: `discount_premium` (cheapness), `yield`. Implemented in
`src/crowdscenario/domains/stock_tw.py`.

| persona | 中文 | herding | polarity | (discount, yield) sensitivity | behavioural-prior source (verify before citing) |
|---|---|---|---|---|---|
| long_term_holder | 存股族 | 0.15 | contra | (0.8, 0.4) | TDCC beneficial-owner counts for 0050/0056 — long-hold + dividend reinvest |
| day_trader | 當沖客 | 0.85 | pro | (0.0, 0.0) | TWSE day-trading statistics — day-trade share of turnover; stop-loss cascades |
| yield_seeker | 殖利率派 | 0.40 | pro | (0.2, 1.0) | TWSE ex-dividend calendar + fund-flow around distribution announcements |
| leveraged_etf_player | 槓桿 ETF 玩家 | 0.70 | pro | (0.0, 0.0) | daily-reset decay + volume spikes in 2x/inverse products under volatility |
| foreign_institutional_lens | 外資視角 | 0.10 | contra | (0.7, 0.2) | TWSE three-institutional-investors daily net buy/sell; index-review flows |
| panic_retail | 恐慌散戶 | 0.90 | pro | (0.0, 0.0) | margin-balance swings as a chase-high / sell-low contrarian proxy |
| ptt_dcard_trendwatch | PTT/Dcard 風向 | 0.95 | pro | (0.0, 0.0) | post-volume / keyword spikes on stock boards around events |
| mom_savings_group | 媽媽存股社團 | 0.35 | contra | (0.6, 0.5) | TDCC regular-savings-plan (定期定額) account growth — sticky on drawdowns |
| main_force_lens | 主力/中實戶 | 0.20 | contra | (0.9, 0.1) | margin/short balances + large-holder concentration |
| dca_newbie | 定期定額新手 | 0.75 | pro | (0.1, 0.1) | broker + new-account and DCA-plan growth; recency bias |

## `PRODUCT_LAUNCH` — product/user cohorts (8 personas, 3 axes)

Axes: `price_change`, `value_delta`, `switching_cost`. A non-finance domain that
deliberately uses a different axis count, proving the roster/axes are pluggable.
Implemented in `src/crowdscenario/domains/product.py`.

| persona | 中文 | herding | polarity | (price, value, switch) sensitivity |
|---|---|---|---|---|
| early_adopter | 嘗鮮玩家 | 0.85 | pro | (0.2, 1.0, 0.1) |
| free_tier_user | 免費用戶 | 0.60 | pro | (0.9, 0.4, 0.3) |
| power_user | 重度用戶 | 0.35 | contra | (0.3, 0.9, 0.7) |
| budget_conscious | 精打細算族 | 0.55 | pro | (1.0, 0.3, 0.2) |
| brand_loyalist | 品牌鐵粉 | 0.20 | contra | (0.2, 0.3, 0.6) |
| competitor_fan | 競品愛好者 | 0.90 | pro | (0.4, 0.6, 0.1) |
| casual_user | 輕度用戶 | 0.30 | contra | (0.3, 0.4, 0.5) |
| community_voice | 社群風向 | 0.95 | pro | (0.5, 0.7, 0.2) |

## How stance is decided (deterministic, scalar-free)

1. A seed-derived **consensus** (`negative | neutral | positive`) sets the baseline lean.
2. `contra` personas fade it; `pro` personas amplify it.
3. Each persona then applies its **own** read of every ordinal axis the pack defines,
   weighted by its per-axis sensitivity — so within one scenario, context-driven
   cohorts can resist (even reverse) a mild consensus while low-sensitivity cohorts
   (weights `0,0,…`) just ride it.
4. The internal lean is thresholded back to a categorical **stance ∈ {-1, 0, +1}**
   before anything leaves the engine. No numeric scalar escapes.

The neutral consensus is rendered to each domain's display labels via the pack's
`consensus_display` map (stock → bearish/neutral/bullish; product → oppose/neutral/
support), but the emitted `crowd_consensus` stays the neutral vocabulary.

## Credibility note

The stock source column names *where* each prior is verifiable (TDCC / TWSE / issuer
disclosures) — pull current numbers from those sources before citing any figure.
Synthetic personas remain **scenario rehearsal, not survey data**: reproducible ≠
validated. This holds for every domain, not just stock.

## Extending to another domain

Ship a sibling `DomainPack`: a new closed persona roster + voices + display names, a
tuple of `Axis` objects (each with a bucket function + tilt table), a per-persona
sensitivity tuple sized to the axes, and a `consensus_display` mapping — all reusing
the same neutral stance vocabulary, the same `CrowdNarrative` contract, and the same
firewall. Never mix domains in one roster. New domain, same cage.
