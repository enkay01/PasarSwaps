# Research notes

The index for this folder. The feature these notes support is [Download the S&P 500 and screen it](https://github.com/enkay01/PasarSwaps/issues/1), which shipped in [pull request #21](https://github.com/enkay01/PasarSwaps/pull/21). The vocabulary is in [CONTEXT.md](../../CONTEXT.md).

## Where this stands

The first Feature shipped on 2026-09-16. `download.py` asks Alpaca Basic for daily Bars over the S&P 500 and writes one Parquet file, and `screen.py` reads that file without touching the network and prints the symbols with a fresh bullish MACD cross on the latest Bar. The Dataset holds 503 symbols from 2017-11-15 to 2026-09-15, because a free key serves less history than Alpaca's pricing page states. yfinance stays as an optional deep-history extra. The Backtest engine is not chosen yet, because the Screen comes first. Cost to start is zero.

Interactive Brokers was dropped. The first research round found that it needs a funded live account before a paper account exists, a gateway process holding a browser login, and that it has no history at all for expired option contracts. The second round found a free Alpaca paper account that needs none of that. The IBKR notes stay here as background.

## The notes

The hobbyist notes are the ones to read. They are written for one person with a laptop.

[Where a hobbyist gets options data](hobbyist/options-data-sources.md) compares twelve sources and points at ThetaData and MarketData.app.

[Where a hobbyist gets market data](hobbyist/market-data-sources.md) compares eleven sources and points at yfinance first, then Alpaca.

[The easiest paper trading and backtesting path](hobbyist/paper-trading-and-backtesting.md) ranks brokers and libraries by setup work and names a five-step path.

The first round is background on the dropped broker. [IBKR API options](ibkr/api-surfaces.md) covers the three ways to connect. [IBKR historical data limits](ibkr/historical-data-limits.md) covers bar sizes, pacing and retention. [IBKR market data subscriptions](ibkr/market-data-subscriptions.md) covers what must be paid before data flows. [IBKR options data](ibkr/options-data.md) covers the expired-contract gap.

Three older notes cover [hobby projects](hobby-algorithmic-trading-builds.md), [Massive request limits](massive-rate-limits-and-batching.md), and [institutional options vendors](credit-spreads/historical-options-and-event-data.md).

## Adding a note

Write the claim, the source link, the date checked, and what is still unknown. Follow `AGENTS.md`. Keep the evidence separate from the decision it led to.
