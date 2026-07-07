# crowd-scenario

> A deterministic, **firewalled**, **domain-pluggable** engine that *rehearses* how a
> synthetic crowd would react to an already-decided event — and is **structurally unable
> to leak a number back into your decision.**

繁體中文版 → [README.zh-TW.md](README.zh-TW.md)

## What it does

You have already made a decision (a rate cut hit, a price hike is shipping). You want to
*rehearse* how a crowd might react to it — not to predict the future, but to pressure-test
your own read against a synthetic second opinion.

`crowd-scenario` takes a bucketed snapshot of the situation and plays out a crowd of
**persona archetypes** — each with its own voice and its own sensitivities — reacting to
the event. It orders them into a **who-moves-first reaction chain** (the fast herders
panic, the slow fundamentals cohorts wait) and emits **one categorical stance**
(`negative | neutral | positive`) plus a readable narrative.

That's it. It decides no number, recommends no action, and never writes back into your
model. It's a **warning light**, not a steering wheel.

```text
   your situation                the engine                    what comes out
 ┌────────────────┐   buckets   ┌──────────────────────┐      ┌───────────────────┐
 │ discount -0.6  │────────────▶│ 10 personas react,   │─────▶│ stance: bullish   │
 │ yield     8.5  │  (numbers   │ ordered who-moves-   │      │ + reaction-chain  │
 │ event: rate cut│   dropped)  │ first, deterministic │      │   narrative       │
 └────────────────┘             └──────────────────────┘      └───────────────────┘
        raw metrics stop here ↑                        no number ever leaves ↑
```

## Why it's powerful

- **The firewall is the product, and it's structural — not discipline.** The engine
  *cannot* leak a decision-grade number, even by accident: raw metrics are dropped at the
  door (only ordinal buckets like `"deep_discount"` get in), and the only thing it can
  emit is a categorical label — there is literally no float field on the output for a
  "just add 0.05" leak to live in. The contract enforces this with explicit checks that
  even survive `python -O`.
- **Deterministic and reproducible.** Same input → byte-identical output, forever. No
  network, no clock, no randomness beyond a hashed seed. You can diff two runs, pin them
  in tests, and trust that a rehearsal is repeatable.
- **Domain-pluggable.** The engine core knows nothing about stocks. A `DomainPack`
  supplies the personas, the axes, and the labels — so the *same* firewalled engine
  rehearses Taiwan retail investors (`STOCK_TW`), a product launch (`PRODUCT_LAUNCH`), or
  any crowd you can model. A bad pack can't even be constructed.
- **LLMs allowed, but never in charge.** The categorical decision is made by the engine
  *before* any language model runs. An optional `FusionNarrator` (2 writers + 1 judge)
  can prettify the prose, but every model output is screened by a deterministic firewall
  scanner, and the emitted stance is **identical** whether an LLM ran or not. The dangerous
  part (the number) is never in the model's hands.
- **Zero runtime dependencies.** Pure standard library. Drops into any codebase without
  pulling a dependency tree.

> **Scenario rehearsal, not a forecast.** Synthetic personas, not real opinion.
> Not backtested. This layer produces narrative only — it decides no number,
> influences no action, and never writes back into a decision.

## How it works (one line)

`make_seed` (raw metrics → bucketed, hashed seed) → `run_scenario` (personas take a
stance, ordered into a reaction chain) → `CrowdNarrative` (one categorical stance +
prose). Optionally, `compose_divergence` diffs the crowd against *your own* read.

The engine core is domain-agnostic. A **`DomainPack`** supplies the persona roster,
the ordinal axes, and the display labels, so the same firewalled engine can rehearse
Taiwan retail investors (`STOCK_TW`), a product launch (`PRODUCT_LAUNCH`), or any
other crowd you can model as a pack.

## Why "firewalled"

The whole point is that this crowd layer **cannot** leak a decision-grade number
into your own analysis, even by accident:

- **Read-side** — it reads only a frozen `ScenarioSeed` carrying *bucketed ordinal
  context* (e.g. `discount_premium -> "deep_discount"`), never a raw price/yield/metric.
- **Write-side** — it emits only a `CrowdNarrative`: a categorical stance
  (`negative | neutral | positive`) + narrative. There is **no numeric scalar** on
  the artifact that anything could sum into a decision total. Each domain renders the
  stance into its own labels for display (stock: `bullish`; product: `support`), but
  the contract value stays the neutral vocabulary.
- **Flag** — `non_authoritative` is hard-wired `True` and asserted in the contract.
- **Pack-side** — a `DomainPack` can only supply *categorical* material. `validate_pack`
  refuses any pack whose parallel tables are misaligned or whose display labels are
  numeric, so a new domain cannot smuggle a scalar back in.

"Sentiment is auxiliary" is enforced by *what the layer is allowed to output*, not
by remembering to be careful. Keep it categorical and it stays a warning layer by
construction. (The contract invariants are locked by `tests/test_contracts.py`.)

## Install

```bash
pip install -e ".[dev]"      # editable + dev tools (pytest, ruff)
```

Zero runtime dependencies — pure standard library.

## Use it from the CLI

```bash
# one rehearsal, stock domain (deterministic; JSON out) — --domain defaults to stock_tw
python -m crowdscenario run --symbol 0056 --scenario 0056_cut

# reshape which cohort leads the chain by time-scale + shock strength
python -m crowdscenario run --symbol 0056 --scenario 升息 --horizon long --intensity severe

# a different domain: rehearse a product launch
python -m crowdscenario run --domain product_launch --symbol big_feature --scenario big_feature

# let the crowd DIRECTION follow the persona majority instead of the seed hash
python -m crowdscenario run --domain product_launch --symbol price_hike --scenario price_hike --consensus-mode aggregate

# feed your OWN raw metrics (JSON) instead of a built-in demo fixture — only their
# ordinal buckets survive into the seed; the raw numbers never cross the firewall
python -m crowdscenario run --symbol MYETF --scenario evt --metrics '{"discount_premium": -0.6, "yield": 8.5}'

# determinism check — compares the FULL artifact (consensus + narrative + persona
# samples + seed_id), and takes --horizon / --intensity like `run` does
python -m crowdscenario verify --symbol 0056 --scenario 0056_cut
python -m crowdscenario verify --symbol 0056 --scenario 升息 --horizon long --intensity severe
```

`--domain {stock_tw,product_launch}` selects the persona/axis pack.
`--horizon {intraday,swing,long}` shifts *who moves first* (intraday → the fastest
herders lead; long → the slow, low-herding cohorts lead). `--intensity {mild,severe}`
widens the tail framing. `--consensus-mode {hashed,aggregate}` chooses how the crowd
*direction* is decided — `hashed` (seed-derived, the default, byte-stable) or
`aggregate` (the persona majority, so a majority-bear roster emits `negative` instead of
a hash-rolled stance). Both are deterministic and scalar-free. `--metrics '<json>'` feeds
your own raw metrics instead of a built-in demo fixture (only their ordinal buckets reach
the seed — raw numbers never cross the firewall); an unknown symbol with no `--metrics`
falls back to neutral input and says so on stderr. `run`'s JSON also reports
`consensus_mode`, `narrator_backend` / `narrator_notes`.

## Use it from Python

```python
from crowdscenario import make_seed, run_scenario, compose_divergence, posture_from_score
from crowdscenario import STOCK_TW, PRODUCT_LAUNCH

# --- stock domain (the default pack) ---
seed = make_seed(
    "0056",
    {"discount_premium": -0.6, "yield": 8.5},   # raw metrics — only their buckets survive
    market_scenario_label="0056_cut",
    horizon="long",
    intensity="severe",
    pack=STOCK_TW,                               # omit to use the default (STOCK_TW)
)
narrative = run_scenario(seed, pack=STOCK_TW)     # deterministic CrowdNarrative
print(narrative.crowd_consensus)                  # 'negative' | 'neutral' | 'positive'
print(STOCK_TW.consensus_display[narrative.crowd_consensus])  # 'bearish'|'neutral'|'bullish'
print(narrative.narrative_md)                     # the reaction-chain story

# --- a different domain: same engine, different pack ---
seed = make_seed(
    "big_feature",
    {"price_change": 0.0, "value_delta": 0.7, "switching_cost": 0.5},
    market_scenario_label="big_feature",
    pack=PRODUCT_LAUNCH,
)
print(run_scenario(seed, pack=PRODUCT_LAUNCH).crowd_consensus)  # neutral vocabulary

# Diff the synthetic crowd against your OWN read (you supply the posture; the
# engine never sees it). Feed it your own composite/score if you have one:
divergence = compose_divergence(narrative, posture_from_score(0.42))
print(divergence.divergence_bucket)               # 'LOW' | 'MEDIUM' | 'HIGH'
```

## Feeding real data

The firewall exists precisely so you *can* feed the crowd layer real, decision-grade
numbers — a sentiment score you scraped, a live discount-to-NAV, a trailing yield —
without any of them leaking back out. `make_seed` buckets each raw metric into an ordinal
label and **drops the number**, so the personas only ever see `"deep_discount"`, never
`-1.5`.

The pattern is dependency injection: you supply a `fetch_metrics(symbol) -> dict` (your
crawler / API / DB), and the engine does the rest. A runnable, offline worked example
ships in [`examples/real_data.py`](examples/real_data.py):

```python
def fetch_metrics(symbol):        # <- your real data layer goes here
    return {"discount_premium": -0.6, "yield": 8.5}

raw = fetch_metrics("0056")       # real numbers live ONLY in this local variable...
seed = make_seed("0056", raw, market_scenario_label="rate_cut", pack=STOCK_TW)
# ...and are gone by here: the seed carries buckets, not numbers.
print(run_scenario(seed, consensus_mode="aggregate").crowd_consensus)
```

```bash
# run the shipped example (needs the package importable)
#   PowerShell:  $env:PYTHONPATH='src'; python examples/real_data.py
#   bash:        PYTHONPATH=src python examples/real_data.py
```

Rehearsal, not a forecast: it decides no number and writes back into no decision.

## Domains & personas

A `DomainPack` is a frozen bundle of a persona roster, N ordinal axes (each with its
own bucket function + tilt table), per-persona sensitivities, and a neutral→display
label mapping. Two packs ship in the box:

- **`STOCK_TW`** — 10 Taiwan retail archetypes over two axes (`discount_premium`,
  `yield`): 存股族 / 當沖客 / 殖利率派 / 槓桿 ETF 玩家 / 外資視角 / 恐慌散戶 /
  PTT·Dcard 風向 / 媽媽存股社團 / 主力·中實戶 / 定期定額新手.
- **`PRODUCT_LAUNCH`** — 8 user cohorts over three axes (`price_change`, `value_delta`,
  `switching_cost`): 嘗鮮玩家 / 免費用戶 / 重度用戶 / 精打細算族 / 品牌鐵粉 /
  競品愛好者 / 輕度用戶 / 社群風向.

Each persona has its own voice and its own sensitivity to the ordinal context, so
within one scenario they diverge rather than flip in lockstep. To add a domain, build
a `DomainPack` (see `src/crowdscenario/domains/product.py` as a worked example) and
pass it to `make_seed`/`run_scenario`. See [`references/personas.md`](references/personas.md).

## Narrating the facts (optional LLM layer)

The **categorical decision is always made by the engine** — deterministically and
firewalled — *before* any narrator runs. A **narrator** only turns those already-decided
facts into prose. It can never change a stance, a consensus, or introduce a number.

- **`DeterministicNarrator`** (default) — offline, stdlib, table-lookup prose. Same
  facts → byte-identical narrative. This is what `run_scenario` uses if you pass nothing.
- **`FusionNarrator`** — **2 writer models + 1 judge model**. The writers each draft a
  narrative over the fixed facts; a rule-based firewall scanner screens **every** model
  output (both writers *and* the judge); the judge picks/merges the survivors. If nothing
  clean survives — or a model errors — it **falls back to the deterministic narrator**.

The models are injected as plain `str -> str` callables, so the core stays
zero-dependency and the whole thing is offline-testable. `run_scenario`'s emitted
`crowd_consensus` and `persona_samples` are identical whichever narrator you use — only
the prose changes.

```python
from crowdscenario import make_seed, run_scenario, FusionNarrator, STOCK_TW

# Bring your own LLM as a str -> str callable (any client works). Here: illustrative fakes.
def writer_a(prompt: str) -> str: return call_your_llm("gpt", prompt)     # your client
def writer_b(prompt: str) -> str: return call_your_llm("claude", prompt)  # your client
def judge(prompt: str) -> str:    return call_your_llm("gemini", prompt)  # your client

narrator = FusionNarrator(writer_a=writer_a, writer_b=writer_b, judge=judge)

seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
result = run_scenario(seed, narrator=narrator)   # LLM prose, engine-decided stance
print(result.crowd_consensus)                    # identical to the deterministic run
print(result.narrative_md)                       # the chosen/merged, firewall-screened prose
```

**Firewall guarantees for the fusion path.** A model output that contains a numeric
market token (price / NAV / NTD / % / yield, in half- *or* full-width digits), an
internal signal encoding (`stance=` / `score=` / `modifier=` / `weight=`), or an order
phrase (買進/賣出/委託單 …) is **rejected, not sanitised** — the scanner
(`crowdscenario.scan_violations`) is deterministic and offline. The fusion prompt hands
personas their stance as words (偏空/中性/偏多), never a bare `-1/0/+1`, so a model has no
numeric signal to echo in the first place. Any leak means that candidate is dropped; the
safe deterministic prose is always available as the floor. The fusion path itself is not
reproducible (LLMs drift), but the emitted `crowd_consensus` **is** — it never comes
from a model.

## Layout

```
src/crowdscenario/
  contracts.py       ScenarioSeed / CrowdNarrative / PersonaReaction / NarrativeDivergence
  domains/
    base.py          DomainPack / Axis / validate_pack — the pluggable-domain protocol
    stock_tw.py      STOCK_TW — the 10 Taiwan retail archetypes (2 axes)
    product.py       PRODUCT_LAUNCH — an 8-cohort product-launch domain (3 axes)
  narrator/
    base.py          NarratorBackend / EngineFacts — the read-only facts hand-off
    firewall.py      scan_violations — the rule-based screen every LLM output must pass
    deterministic.py DeterministicNarrator — the default offline table-lookup prose
    fusion.py        FusionNarrator — 2 writer LLMs + 1 judge LLM, firewall-screened
  seed.py            make_seed — raw metrics -> bucketed, hashed ScenarioSeed (per pack)
  engine.py          run_scenario — reads a pack + narrator: stance logic + reaction chain
  composer.py        compose_divergence — crowd-vs-your-own read (report time)
  cli.py             python -m crowdscenario run | verify  (--domain ...)
references/          personas.md (roster), firewall.md (the contract)
tests/               contract + engine invariants + narrator/fusion (offline, fakes)
```

## Test

```bash
pytest -q          # engine + firewall contracts + narrator/fusion + property-based invariants
ruff check .       # lint
```

The suite covers example-based tests *and* hypothesis property tests (determinism, always
categorical output, no raw-number leak, monotonicity). Firewall contracts are additionally
asserted under `python -O` in CI, so optimize mode can never strip them.

## Provenance

The crowd-scenario idea is a clean-room distillation (idea only). It began as the
non-authoritative FACE side-rail of a larger research-desk project and was extracted
here as a standalone, dependency-free engine.

## Licence

MIT.
