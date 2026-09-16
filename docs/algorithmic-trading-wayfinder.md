# Algorithmic trading research map

Status: research only. This file is the reading index. Decisions and open tickets live on the [issue map](https://github.com/enkay01/PasarSwaps/issues/1).

## Where this stands

The stack is chosen. yfinance for daily equity and ETF history, ThetaData or MarketData.app for options, backtesting.py or vectorbt for the backtest, and an Alpaca Paper Only account with `alpaca-py` for paper. Cost to start is zero.

Interactive Brokers is dropped. The first research round found that it needs a funded live account before a paper account exists, a gateway process holding a browser login, and that it has no history at all for expired option contracts. The second round found a free Alpaca paper account that needs none of that. The IBKR notes stay in the repo as background.

One question is left open, about what shape the stored data takes.

## The notes

The hobbyist notes are the ones to read. They are written for one person with a laptop.

[Where a hobbyist gets options data](research/hobbyist/options-data-sources.md) compares twelve sources and points at ThetaData and MarketData.app.

[Where a hobbyist gets market data](research/hobbyist/market-data-sources.md) compares eleven sources and points at yfinance first, then Alpaca.

[The easiest paper trading and backtesting path](research/hobbyist/paper-trading-and-backtesting.md) ranks brokers and libraries by setup work and names a five-step path.

The first round is background on the dropped broker. [IBKR API options](research/ibkr/api-surfaces.md) covers the three ways to connect. [IBKR historical data limits](research/ibkr/historical-data-limits.md) covers bar sizes, pacing and retention. [IBKR market data subscriptions](research/ibkr/market-data-subscriptions.md) covers what must be paid before data flows. [IBKR options data](research/ibkr/options-data.md) covers the expired-contract gap.

Three older notes cover [hobby projects](research/hobby-algorithmic-trading-builds.md), [Massive request limits](research/massive-rate-limits-and-batching.md), and [institutional options vendors](research/credit-spreads/historical-options-and-event-data.md).

## Open tickets

| Ticket | Type | Question |
| --- | --- | --- |
| [#15](https://github.com/enkay01/PasarSwaps/issues/15) | decision | What shape stored data takes so one pull serves every backtest it can support |

## Adding a note

Write the claim, the source link, the date checked, and what is still unknown. Follow `AGENTS.md`. Keep a product decision separate from the evidence behind it, and put the decision on the issue map rather than here.
