# Research notes

The index for this folder. The feature these notes support is [Hobbyist trading lab](https://github.com/enkay01/PasarSwaps/issues/1). The vocabulary is in [CONTEXT.md](../../CONTEXT.md).

## Where this stands

The stack is chosen. yfinance for daily equity and ETF history, ThetaData or MarketData.app for options, backtesting.py or vectorbt for the backtest, and an Alpaca Paper Only account with `alpaca-py` for paper. Cost to start is zero.

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
