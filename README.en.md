**English** | [中文](README.md)

# Heartbeat Perception 📈

Heartbeat Perception is an open-source Skill that lets AI Agents mine macro-event trends from massive financial data.

Works with OpenClaw / Claude Code / Cursor / Codex.

We live in an era of extreme noise. Social media is flooded with emotional predictions — someone says housing is about to crash, someone says gold is going to the moon, someone says war breaks out tomorrow. These opinions chase crowd sentiment rather than rational analysis grounded in objective data.

But trading data is different.

Price is absolutely rational — when someone puts real money on an outcome, they think a lot harder than when they post a short video.

This is the core insight of the Efficient Market Hypothesis: **all public information is already priced in. Everything is in the chart.**

Heartbeat Perception turns this insight into an executable tool. It plugs into 14 authoritative financial data sources — **from prediction markets like Polymarket and Kalshi, to US Treasury yield curves, CFTC institutional positioning, SEC insider trades, central bank rates, crypto derivatives, CNN Fear & Greed market sentiment, and CME FedWatch rate probabilities.**

It doesn't read newspapers, news articles, short videos, or podcasts. It answers questions about housing prices, gold trends, Bitcoin cycles, and military conflict probabilities purely through price signals mined from financial data — delivering structured probability estimates with full reasoning chains.

In a sense, it's a Heartbeat Perception for the new era.

## What can it answer?

- "What's the probability of WW3?"
- "Will there be a US recession this year?"
- "Is AI in a bubble?"
- "Is now a good time to buy gold?"
- "Has Bitcoin bottomed?"
- "Is NVDA options premium overpriced?"

If there's a market pricing an outcome, Heartbeat Perception can give you a probability estimate backed by trading data.

## Data Sources

| Provider | Data Type | Purpose |
|----------|-----------|---------|
| Polymarket | Prediction market contracts | Event probability pricing |
| Kalshi | SEC-regulated binary contracts | US political/economic events |
| Yahoo Finance | Stocks/ETFs/FX/Commodities | Price history and trends |
| Deribit | Crypto derivatives | Futures term structure, options IV |
| US Treasury | Treasury yields + exchange rates | Yield curves, inflation expectations, fiscal FX rates |
| CFTC COT | Futures positioning | Institutional direction (smart money) |
| CoinGecko | Crypto spot + global overview | BTC/ETH price, market cap, BTC dominance, market rankings |
| SEC EDGAR | Insider trades + full-text search | Form 4 buy/sell signals, keyword filing search |
| BIS | Central bank data | Policy rates, credit-to-GDP gaps |
| World Bank | Development indicators | GDP, population, trade |
| Yahoo Finance Options | US options chains + Greeks | IV, delta/gamma/theta/vega, put/call ratio, max pain, IV skew |
| CNN Fear & Greed | Market sentiment | 7 price signals composite → 0-100 fear/greed score |
| CME FedWatch | Rate probabilities | FOMC rate change implied from Fed Funds futures |
| Web Search | Web search + page fetch | VIX, CDS supplementary data, arbitrary page text extraction |

All APIs are free and require no API keys.

## Installation

### OpenClaw

```bash
clawhub install Heartbeat Perception
```

### Other AI Agents (Claude Code / Cursor / Codex / ...)

Just tell your agent:

> Install this open-source project and read SKILL.md as your working instructions: https://github.com/YOUZ27/Heartbeat-Perception

The agent will clone the repo, read the methodology, and call the providers on its own.

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager, used to run skill scripts at runtime
- 12 out of 14 data sources have zero external dependencies (pure Python stdlib). Price history and options chain analysis require an extra install:

```bash
uv pip install yfinance
```

## How It Works

1. **Understand the question** — decompose into core variables, time window, and priceability
2. **Select signals** — pick 3+ independent data sources based on question type
3. **Fetch in parallel** — use `gather()` to call multiple providers concurrently
4. **Contradiction analysis** — find disagreements between markets, explain why both can be right
5. **Output report** — structured multi-layer signal tables + probability estimates + scenario analysis

## Project Structure

```
Heartbeat Perception/
├── SKILL.md                # Skill definition (read by OpenClaw)
├── digital_oracle/         # Python source code
│   ├── concurrent.py       # Parallel execution utilities
│   ├── http.py             # HTTP client abstraction
│   ├── combination.py      # Probability combination (linear/logarithmic pool)
│   ├── signal_quality.py   # Signal quality assessment framework
│   ├── snapshots.py        # HTTP response recording/replay (for tests)
│   └── providers/          # 14 data providers
├── references/             # API reference
│   ├── providers.md        # Provider API docs
│   └── symbols.md          # Trading symbol directory
├── scripts/                # Demo scripts
├── tests/                  # Unit tests + fixtures
└── ITERATION_PLAN.md       # Iteration plan
```

## Design Principles

- **Zero dependencies first** — 12/14 providers use only the Python standard library, no `pip install` needed
- **Dependency injection** — all providers accept an optional `http_client` parameter for easy testing
- **Partial failure tolerance** — one data source going down doesn't break the rest
- **Snapshot testing** — record real HTTP responses, run tests offline in CI

## License

MIT © 2026 komako-workshop — see [LICENSE](LICENSE).