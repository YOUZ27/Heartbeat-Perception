---
name: digital-oracle
version: 1.0.4
description: "Answer prediction questions using market trading data, not opinions. Use when the user asks probability questions about geopolitics, economics, markets, industries, or any topic where real money is being traded on the outcome. Examples: 'What's the probability of WW3?', 'Will there be a recession?', 'Is AI in a bubble?', 'When will the Russia-Ukraine war end?', 'Is it a good time to buy gold?', 'Will SPY drop 5% this month?', 'Is NVDA options premium overpriced?'. The skill reads prices from prediction markets, commodities, equities, options chains, derivatives, yield curves, and currencies, then cross-validates multiple signals to produce a structured probability report."
metadata: { "openclaw": { "emoji": "📈", "requires": { "bins": ["uv"] } } }
---

# digital-oracle

> Markets are efficient. Price contains all public information. Reading price = reading market consensus.

## Methodology

**Answer questions using only market trading data — no news, opinions, or statistical reports as causal evidence.** If something is true, some market has already priced it in.

Five iron rules:

1. **Trading data only** — prices, volume, open interest, spreads, premiums. Never cite analyst opinions.
2. **Explicit reasoning from price to judgment** — explain clearly "why this price answers this question."
3. **Multi-signal cross-validation** — never conclude from a single signal. At least 3 independent dimensions.
4. **Label the time horizon of each signal** — options price 3 months, equipment orders price 3 years — don't mix them in the same vote.
5. **Structured output** — the final report must follow the Step 5 template: layered signal tables → contradiction analysis → probability scenarios → signal consistency assessment. Do not substitute prose for structured reporting.

## Workflow

### Step 1: Understand the question

Decompose the user's question into:
- **Core variable**: What event or trend?
- **Time window**: Is the user asking about 3 months, 1 year, or 5 years?
- **Priceability**: Is there real money being traded on this outcome?

### Step 2: Select signals

Based on question type, select from the signal menu below. **Don't use just one category — cover at least 3.**

#### Geopolitical conflict / War risk
- Polymarket: Search for related event contracts (ceasefire, invasion, regime change, declaration of war)
- Kalshi: Search for related binary contracts
- Safe-haven assets: Gold (GC=F), silver (SI=F), Swiss franc (USDCHF=X)
- Conflict proxies: Crude oil (CL=F), natural gas (NG=F), wheat (ZW=F), defense ETF (ITA), defense stocks
- Risk ratios: Copper/Gold ratio (risk-off indicator), Gold/Silver ratio
- CFTC COT: Institutional positioning changes in crude/gold/wheat (which direction is smart money betting)
- BIS: Central bank policy rate trends in relevant countries
- FearGreedProvider: CNN Fear & Greed Index (composite of 7 price signals)
- Web search: VIX, MOVE index, sovereign CDS, war risk premiums, BDI freight rates, high-yield OAS
- Currencies: Currency pairs of relevant countries (e.g. USDRUB=X, USDCNY=X)
- Country ETFs: Asset flows in relevant countries (e.g. FXI, EWY)

#### Economic recession / Macro cycle
- Treasury: Yield curve shape (10Y-2Y spread, 10Y-3M spread), real rates, breakeven inflation
- YahooPriceProvider: SPY, copper (HG=F), crude oil (CL=F), price trends
- Risk ratios: Copper/Gold ratio
- CFTC COT: Speculative net positions in copper/crude (is managed money bullish or bearish)
- BIS: Credit-to-GDP gap (credit overheating = late cycle), policy rate directions
- World Bank: GDP growth rate historical trends, cross-country comparisons
- Deribit: BTC futures basis (risk appetite proxy)
- CoinGecko: Crypto total market cap + BTC dominance (risk appetite proxy)
- FearGreedProvider: CNN Fear & Greed Index (7 price signals composite → 0-100)
- CMEFedWatchProvider: Market-implied FOMC rate change probabilities from 30-Day Fed Funds futures
- Polymarket: Recession-related contracts, central bank rate path
- Currencies: DXY/dollar strength, emerging market currencies
- Web search: High-yield bond spread (HY OAS), TED spread, MOVE index, TTF gas, BDI freight rates

#### Industry cycle / Bubble assessment
- YahooPriceProvider: Industry leader stock trends, sector ETFs
- Find the industry's "single-purpose commodity" (e.g. GPU rental price → AI, rebar → construction)
- Upstream equipment maker orders/stock price (e.g. ASML → semiconductors)
- Leader company valuation discount (e.g. TSMC vs peers → Taiwan Strait risk pricing)
- EDGAR: Industry leader insider trading cadence (Form 4) — concentrated selling = bearish signal. Also use `search_filings()` for keyword-based filing search
- CFTC COT: Institutional positioning changes in related commodities
- CoinGecko: For crypto industry, look at BTC/ETH/altcoin market cap distribution
- Web search: VC funding concentration, leveraged ETF concentration, margin debt levels
- Deribit: Implied volatility of related crypto assets

#### Asset pricing / Whether to buy
- YahooPriceProvider: Target asset price trend (daily/weekly/monthly)
- Relative price changes of correlated assets (divergence between two commodities = structural signal)
- Treasury: Risk-free rate as valuation anchor
- YFinanceProvider: Options chain (IV, put/call ratio, max pain, Greeks, implied move, IV skew)
- EDGAR: Insider selling cadence (heavy Form 4 selling = insiders bearish). `search_filings()` for extra context
- CFTC COT: Speculative vs commercial net position divergence for commodity assets (use `mm_net`, `prod_net`, `smart_money_direction`, `speculative_ratio`)
- CoinGecko: For crypto assets, check market cap, ATH/ATL distance, 24h volatility. Use `get_global()` for BTC dominance + total market cap
- Deribit: Crypto options chain (implied volatility = market's expected range)
- Polymarket/Kalshi: Probability pricing of related events
- FearGreedProvider: CNN Fear & Greed composite score (momentum, breadth, VIX, put/call, junk bond demand, volatility, safe haven)
- Web search: VIX, corporate bond issuance volume, analyst rating distribution

#### Stock/Options analysis / Crash probability
- YFinanceProvider: Options chain → ATM IV (expected volatility), IV skew (upside/downside fear asymmetry), put/call ratio (bull/bear sentiment), max pain (market maker profit zone), implied move (expected price range), Greeks via `black_scholes_greeks()` (delta ≈ ITM probability, gamma, theta, vega)
- YahooPriceProvider: Underlying historical price → realized volatility (compare vs implied volatility to judge options premium)
- Kalshi: SPY/NASDAQ price range markets → direct probability pricing
- CFTC COT: S&P 500/VIX futures positioning → institutional direction (use `smart_money_direction`, `commercial_hedge_intensity`)
- Defensive rotation: XLY (cyclical) vs XLP (defensive) vs XLU (utilities) relative performance → market defensiveness
- Treasury: Yield curve shape → recession signal
- FearGreedProvider: CNN Fear & Greed Index
- Web search: VIX level, margin debt level, leveraged ETF concentration

**Available trading symbols directory:** See [references/symbols.md](references/symbols.md)
**Provider API reference:** See [references/providers.md](references/providers.md)

### Step 3: Signal routing

Before fetching data, evaluate each candidate signal from Step 2 against three criteria:

1. **Relevance**: Can this signal actually answer the user's specific question? (e.g., asking about Taiwan → skip CoinGecko)
2. **Time match**: Does the signal's pricing horizon match the question's time window? (e.g., asking about 3 months → skip World Bank GDP which lags 1-2 years)
3. **Information increment**: Does this signal provide an independent perspective not already covered by other signals? Avoid redundancy, keep complementary signals.

Only keep signals that pass all three checks. This reduces noise, saves fetch time, and produces cleaner analysis.

### Step 4: Fetch data

Use digital-oracle's Python providers to fetch structured data, calling all sources in parallel with `gather()` (including web search):

```python
from digital_oracle import (
    PolymarketProvider, PolymarketEventQuery,
    KalshiProvider, KalshiMarketQuery,
    YahooPriceProvider, PriceHistoryQuery,   # requires uv pip install yfinance
    DeribitProvider, DeribitFuturesCurveQuery, DeribitOptionChainQuery,
    USTreasuryProvider, YieldCurveQuery, ExchangeRateQuery,
    WebSearchProvider, WebSearchQuery, WebPageQuery,
    CftcCotProvider, CftcCotQuery,
    CoinGeckoProvider, CoinGeckoPriceQuery, CoinGeckoMarketQuery,
    EdgarProvider, EdgarInsiderQuery, EdgarSearchQuery,
    BisProvider, BisRateQuery, BisCreditGapQuery,
    WorldBankProvider, WorldBankQuery,
    YFinanceProvider, OptionsChainQuery,      # requires uv pip install yfinance
    FearGreedProvider,
    CMEFedWatchProvider,
    # Probability combination tools
    linear_pool, logarithmic_pool,
    # Signal quality assessment
    SignalQuality, PROBABILITY_PHYSICAL, PROBABILITY_RISK_NEUTRAL, PROBABILITY_NAIVE_MIDPOINT,
    gather,
)

pm = PolymarketProvider()
kalshi = KalshiProvider()
yahoo = YahooPriceProvider()  # requires uv pip install yfinance
deribit = DeribitProvider()
treasury = USTreasuryProvider()
web = WebSearchProvider()
cftc = CftcCotProvider()
coingecko = CoinGeckoProvider()
edgar = EdgarProvider(user_email="you@example.com")  # SEC requires email in User-Agent, otherwise 403
bis = BisProvider()
wb = WorldBankProvider()
yf = YFinanceProvider()  # requires uv pip install yfinance
fear_greed = FearGreedProvider()
fedwatch = CMEFedWatchProvider()

result = gather({
    "pm_events": lambda: pm.list_events(PolymarketEventQuery(
        slug_contains="...", limit=10,
        tag_slug=None,          # server-side tag filter (e.g. "bitcoin", "ukraine")
        title_contains=None,    # client-side title keyword filter
    )),
    "yield_curve": lambda: treasury.latest_yield_curve(),
    "gold": lambda: yahoo.get_history(PriceHistoryQuery(symbol="GC=F", limit=30)),
    # Institutional positioning
    "gold_cot": lambda: cftc.list_reports(CftcCotQuery(commodity_name="GOLD", limit=4)),
    # Crypto market sentiment
    "crypto": lambda: coingecko.get_prices(CoinGeckoPriceQuery(coin_ids=("bitcoin", "ethereum"))),
    # Crypto global market overview
    "crypto_global": lambda: coingecko.get_global(),
    # Crypto market rankings
    "crypto_markets": lambda: coingecko.list_markets(CoinGeckoMarketQuery(per_page=10)),
    # Insider trades
    "insider": lambda: edgar.get_insider_transactions(EdgarInsiderQuery(ticker="AAPL", limit=10)),
    # EDGAR full-text filing search
    "edgar_search": lambda: edgar.search_filings(EdgarSearchQuery(
        query="artificial intelligence risk",
        forms="10-K",
        date_start="2025-01-01",
        limit=10,
    )),
    # Central bank policy rates
    "rates": lambda: bis.get_policy_rates(BisRateQuery(countries=("US", "CN"), start_year=2023)),
    # Credit-to-GDP gap (credit overheating indicator)
    "credit_gap": lambda: bis.get_credit_to_gdp(BisCreditGapQuery(countries=("US", "CN"), start_year=2015)),
    # GDP data
    "gdp": lambda: wb.get_indicator(WorldBankQuery(indicator="NY.GDP.MKTP.CD", countries=("US", "CN"))),
    # BTC futures term structure (risk appetite proxy)
    "btc_futures": lambda: deribit.get_futures_term_structure(DeribitFuturesCurveQuery(currency="BTC")),
    # BTC options chain (implied volatility)
    "btc_options": lambda: deribit.get_option_chain(DeribitOptionChainQuery(currency="BTC")),
    # Kalshi event markets (use event_ticker or series_ticker, not keyword search)
    "kalshi_fed": lambda: kalshi.list_markets(KalshiMarketQuery(series_ticker="KXFED", limit=10)),
    # Treasury exchange rates
    "exchange_rates": lambda: treasury.list_exchange_rates(ExchangeRateQuery(
        countries=("China", "Japan"), limit=20,
    )),
    # Options chain (with Black-Scholes Greeks)
    "spy_options": lambda: yf.get_chain(OptionsChainQuery(ticker="SPY", expiration="2026-04-17")),
    # CNN Fear & Greed (composite of 7 price signals)
    "fear_greed": lambda: fear_greed.get_index(),
    # CME FedWatch (implied rate probabilities from futures)
    "fedwatch": lambda: fedwatch.get_probabilities(),
    # Web search runs in parallel with structured providers
    "vix": lambda: web.search("VIX index current level"),
    "hy_spread": lambda: web.search("US high yield bond spread OAS"),
})

# Partial failures don't affect other results
curve = result.get("yield_curve")
vix_info = result.get_or("vix", None)  # WebSearchResult — use .text() to render
crypto_global = result.get_or("crypto_global", None)

# Options data usage
chain = result.get_or("spy_options", None)
if chain:
    print(f"ATM IV: {chain.atm_iv:.1%}, Implied move: {chain.implied_move():.1%}")
    print(f"Put/Call OI ratio: {chain.put_call_oi_ratio:.2f}")
    print(f"Max pain: {chain.max_pain()}")
    print(f"IV skew (25-delta): {chain.iv_skew(delta_target=0.25)}")

# COT report analysis
cot_reports = result.get("gold_cot")
for r in cot_reports:
    print(f"Date: {r.report_date}, MM Net: {r.mm_net}, Direction: {r.smart_money_direction}")
    print(f"  Speculative ratio: {r.speculative_ratio:.2%}")
    print(f"  Commercial hedge intensity: {r.commercial_hedge_intensity:.2%}")

# Probability combination for multi-signal synthesis
synth = linear_pool([
    (0.62, 1.0),  # (probability, weight)
    (0.58, 0.8),
    (0.55, 0.7),
])
print(f"Combined probability: {synth.value:.1%}, Confidence: {synth.confidence:.2f}")

# Yield curve analysis
curve = result.get_or("yield_curve", None)
if curve:
    print(f"10Y-2Y spread: {curve.spread('10Y', '2Y'):.4f}")
    print(f"Is inverted: {curve.is_inverted}")
    print(f"Inversion depth: {curve.inversion_depth_bps:.0f} bps")
    print(f"Steepness (30Y-2Y): {curve.steepness_bps:.0f} bps")

# Web search advanced usage
search_result = web.search(WebSearchQuery(query="MOVE index current", max_results=3))
text_block = search_result.text()  # formatted for LLM consumption
# Fetch full page content
page = web.fetch_page(WebPageQuery(url="https://example.com/financial-data", max_chars=16000))
print(f"Page: {page.title}, truncated: {page.truncated}")

# EDGAR search
search_hits = result.get_or("edgar_search", [])
for hit in search_hits:
    print(f"{hit.entity_name} — {hit.form_type} ({hit.file_date}): {hit.description[:100]}")

# Deribit options chain
btc_chain = result.get_or("btc_options", None)
if btc_chain:
    atm = btc_chain.atm_strike()
    if atm:
        print(f"ATM strike: {atm.strike}, Call IV: {atm.call.mark_iv if atm.call else None}")
```

**All 14 Providers:**

| Provider | Data Type | Purpose | Dependency |
|----------|-----------|---------|------------|
| PolymarketProvider | Prediction market contracts | Event probability pricing | stdlib |
| KalshiProvider | Binary contracts | US regulated event contracts | stdlib |
| YahooPriceProvider | Price history | Stocks/ETFs/FX/Commodities | yfinance |
| DeribitProvider | Crypto derivatives | Futures term structure, options IV, order book | stdlib |
| USTreasuryProvider | Treasury yields + exchange rates | Yield curves, inflation expectations, fiscal FX rates | stdlib |
| WebSearchProvider | Web search + page fetch | VIX/MOVE/CDS/BDI supplementary data | stdlib |
| CftcCotProvider | Futures positioning | Institutional direction (smart money) | stdlib |
| CoinGeckoProvider | Crypto spot + global + rankings | BTC/ETH price, market cap, dominance, market rankings | stdlib |
| EdgarProvider | SEC filings + full-text search | Insider trades Form 4, keyword filing search | stdlib |
| BisProvider | Central bank data | Policy rates, credit-to-GDP gap | stdlib |
| WorldBankProvider | Development indicators | GDP, population, trade, macro data | stdlib |
| YFinanceProvider | US options chains + Greeks | IV, Greeks (delta/gamma/theta/vega), put/call ratio, max pain, IV skew | yfinance |
| FearGreedProvider | Market sentiment | CNN 7-signal composite → 0-100 score | stdlib |
| CMEFedWatchProvider | Rate probabilities | FOMC rate change implied from futures | stdlib |

> 12 out of 14 providers have zero external dependencies and zero API keys. YahooPriceProvider and YFinanceProvider require `pip install yfinance`.

### Step 5: Data analysis

This is the key to report quality. Don't just summarize data — derive judgment from data.

Four analysis dimensions:

1. **Signal interpretation**: What is each data point saying? Derive meaning from price. Not "gold up 3%" but "the market is pricing in tail risk." e.g., Copper/Gold ratio declining → industrial demand weaker than safe-haven demand → risk-off.

2. **Cross-validation**: Which signals point in the same direction (resonance)? Which signals disagree (divergence)? Divergence itself is a high-value signal. e.g., gold says "disaster" but equities say "fine" → two markets pricing different time windows.

3. **Time alignment**: Group signals by their pricing horizon. Don't mix signals from different time windows in the same vote.
   - Short-term (3-12mo): Prediction market contracts, VIX/MOVE, price reaction patterns, executive selling
   - Medium-term (1-3yr): Leader revenue consensus, CapEx plans, VC concentration, leverage concentration
   - Long-term (3-10yr): Equipment maker orders, irreversible capital allocation, ultra-long infrastructure investment
   - Short-term bearish + long-term bullish ≠ contradiction, = S-curve inflection

4. **Weight judgment**: Not all signals are equally reliable. Signals backed by real money > surveys. Liquid markets > illiquid markets. Direct pricing > indirect proxies. e.g., Polymarket high-liquidity contract > CDS quotes (slow updates, low liquidity).

**Probability combination tools:** Use `linear_pool()` (weighted average) or `logarithmic_pool()` (geometric mean of odds ratios, naturally down-weights divergent signals) to synthesize probabilities from multiple sources into a single estimate with a confidence score. See [signal_quality.py] for `SignalQuality` assessment and probability measure classification (`PROBABILITY_PHYSICAL` vs `PROBABILITY_RISK_NEUTRAL` vs `PROBABILITY_NAIVE_MIDPOINT`).

**Core principle: Don't vote by majority.** When signals diverge:
- Check the time dimension first — different signals price different future windows
- Look for "two things happening at once" — old economy Japanification + new economy boom can coexist
- Consider "direction right but timing wrong" — long-term bullish but short-term overheated → wait for a pullback

### Step 6: Output report

**Must follow this structure.** You can adjust the number of layers and wording, but the four main sections (data summary, analysis, probability estimates, conclusion) cannot be omitted or merged into prose paragraphs:

```markdown
# [Question Title]: Multi-Signal Synthesis

## Data Summary

### Layer 1: [Most direct signal source]
| Signal | Data | What it's saying |
|--------|------|-----------------|
(table, one signal per row, third column is reasoning from price to meaning)

### Layer 2: [Secondary signal source]
(same format)

### Layer N: ...
(as needed, typically 3-5 layers)

## Analysis

### Resonance signals
(which signals point in the same direction, and what judgment they form)

### Key divergences
(A says X, B says Y → explain why + who is more credible)

### Time stratification
(what do short-term / medium-term / long-term signals each point to)

## Probability Estimates
| Scenario | Probability | Basis |
|----------|-------------|-------|

### Most likely path: [one-sentence summary]
**Core logic chain:** (2-3 paragraphs, reasoning from data to conclusion)

## Conclusion

> [One-sentence summary, preferably including a specific probability estimate]

### Sub-conclusions
| Dimension | Judgment | Confidence |
|-----------|----------|------------|
| Short-term (6-12mo) | ... | High/Medium/Low |
| Medium-term (1-3yr) | ... | High/Medium/Low |
| Long-term (3-5yr) | ... | High/Medium/Low |
| Systemic risk | ... | High/Medium/Low |
(adjust dimensions to match the question — e.g., replace "systemic risk" with whatever dimension is most relevant)

### Risk factors
- **Upside risk:** what scenario would make things better than expected
- **Downside risk:** what scenario would make things worse than expected

### Signals to monitor
| Signal | Current value | Threshold | Meaning |
|--------|--------------|-----------|---------|
| ... | ... | if crosses X | then Y |
(3-5 concrete signals with specific trigger levels and what they would imply)

---
*Data sources: [list all structured and web data sources]*
*Fetched at: [date]*
```

## Notes

- Polymarket `slug_contains` search is fuzzy — filter results by title keywords after fetching. Use `tag_slug` for server-side tag filtering (e.g. "bitcoin", "ukraine", "taiwan") and `title_contains` for client-side title keyword filtering.
- YahooPriceProvider uses Yahoo Finance symbols: futures use `=F` suffix (e.g. `GC=F`, `CL=F`, `HG=F`), forex uses `=X` suffix (e.g. `EURUSD=X`), US stocks/ETFs use plain tickers (e.g. `SPY`, `LMT`)
- YahooPriceProvider requires `yfinance` — install with `uv pip install --target .deps yfinance`
- European stocks available on Yahoo Finance with exchange suffix (e.g. `RHM.DE` for Rheinmetall, `BA.L` for BAE Systems)
- Prediction market contracts vary in liquidity — contracts with volume < USD 100K should be discounted
- Different signals update at different frequencies: prediction markets real-time, Yahoo Finance daily delayed, Treasury weekly
- CFTC COT updates Tuesday, published Friday. commodity_name uses uppercase ("GOLD", "CRUDE OIL", "S&P 500")
- CftcCotReport provides computed properties: `mm_net` (speculative net position), `prod_net` (commercial net position), `smart_money_direction` ("bullish"/"bearish"/"neutral"), `commercial_hedge_intensity` (fraction of OI), `speculative_ratio` (|mm_net|/OI)
- CoinGecko free API has rate limits (~10-30 req/min) — don't pack too many CoinGecko calls in gather. Use `get_global()` for macro overview (total market cap, BTC/ETH dominance), `list_markets()` for market cap rankings, `get_prices()` for specific coin data
- EDGAR requires `EdgarProvider(user_email="you@example.com")` — SEC requires email in User-Agent, otherwise 403. First call parses ticker→CIK mapping, slightly slow. Use `search_filings(EdgarSearchQuery(...))` for keyword-based full-text search across SEC filings with optional form type and date filters
- BIS data updates infrequently (monthly/quarterly) — suitable for long-term trends, not short-term trading. `get_credit_to_gdp(BisCreditGapQuery(...))` returns credit-to-GDP gap: gap_pct > 10 = credit overheating warning (BIS threshold)
- World Bank GDP data typically lags 1-2 years — latest year may return `None`
- YFinance requires `uv pip install yfinance` (auto-installs pandas). After-hours IV may be inaccurate (bid/ask = 0) — use during market hours
- YFinance `get_chain()` auto-computes Black-Scholes Greeks (pure stdlib `math.erf`, no scipy needed). Use `black_scholes_greeks(S, K, T, r, sigma, option_type)` standalone for custom pricing. Greeks include: delta (≈ P(ITM)), gamma (delta sensitivity), theta (daily decay), vega (per 1pp IV change)
- `OptionsChain` provides: `atm_iv`, `implied_move()` (ATM straddle / underlying), `put_call_volume_ratio`, `put_call_oi_ratio`, `max_pain()` (market maker profit-maximizing strike), `iv_skew(delta_target=0.25)` (OTM put IV - OTM call IV, positive = downside fear premium)
- Absolute value of put delta ≈ probability of that strike being ITM at expiration (rough estimate)
- Put/Call ratio > 1.5 is typically bearish, but as a contrarian indicator, extreme values (> 3) may signal a bottom
- Max pain is the strike price maximizing market maker profit — actual expiration price often converges toward max pain
- Kalshi does NOT support keyword search — use `series_ticker` or `event_ticker` to filter markets. Find tickers by browsing [kalshi.com](https://kalshi.com) or listing markets without filters first. Common series: `KXFED` (Fed rates), `KXINX` (S&P 500 range), `KXGDP` (GDP). Order book supports dual format parsing (`orderbook_fp` and `orderbook`) with automatic cents-unit fallback
- Deribit futures method is `get_futures_term_structure()`, not `get_futures_curve()`. Option chain method is `get_option_chain(DeribitOptionChainQuery(currency="BTC", expiration_label="27MAR26"))` — omit expiration_label for nearest expiry. DeribitBookSummary includes `mark_iv` for implied volatility
- DeribitFuturesTermStructure provides: `structure_type` ("contango"/"backwardation"/"flat"), `perpetual()`, `contango_points`, `backwardation_points`. Each DeribitFutureTermPoint includes `basis_vs_perpetual` and `annualized_basis_vs_perpetual`
- FearGreedProvider has no API key requirement. Returns a single composite score (0-100) synthesizing 7 market price signals: stock momentum, breadth, VIX, put/call ratio, junk bond demand, volatility, safe haven demand. Score < 25 = Extreme Fear, > 75 = Extreme Greed. Also includes `previous_close`, `one_week_ago`, `one_month_ago`, `one_year_ago` for trend analysis
- CMEFedWatchProvider has no API key requirement. Returns implied rate change probabilities for upcoming FOMC meetings, derived from 30-day Fed Funds futures prices. Note: the CME endpoint may occasionally be unavailable or change format — if it fails, fall back to Kalshi `KXFED` series for rate probabilities. Response parsing is resilient to multiple JSON shapes (list, nested object, snake_case/camelCase)
- WebSearchProvider uses DuckDuckGo (zero API keys), with global rate limiting (serialised requests, 2s minimum interval), CAPTCHA detection with retry/backoff (up to 3 attempts), and regex fallback parser for DDG result extraction
- WebSearchProvider `search()` accepts both a string and `WebSearchQuery(query=..., max_results=5)`. `WebSearchResult.text()` renders results as readable text for LLM consumption. `fetch_page(WebPageQuery(url=..., max_chars=8000))` extracts text content from any URL with configurable truncation
- USTreasuryProvider now supports `list_exchange_rates(ExchangeRateQuery(...))` for Treasury fiscal exchange rate data (country, currency, record_date filters)
- StooqProvider is a backward-compatible wrapper that maps legacy Stooq symbols to Yahoo Finance symbols and delegates to YahooPriceProvider internally
- When reporting dollar amounts, use `USD` instead of `$` to avoid markdown renderers interpreting `$...$` as LaTeX