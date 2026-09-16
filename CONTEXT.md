# PasarSwaps

A research notebook for a one-person algorithmic trading project. This file fixes the words. Use these words in notes, tickets, and code comments, and do not swap in synonyms.

## Trading

| Word | Meaning | Do not use |
| --- | --- | --- |
| Bar | One price interval for one instrument, with open, high, low, close and volume. | candle, OHLC row |
| Raw close | The close price as traded, with no adjustment. | unadjusted close |
| Adjusted close | The close price after the source applies dividends and splits. | adj close, total return price |
| Option contract | One underlying, one expiry, one strike and one right. | option, series |
| Option chain | The set of option contracts for one underlying on one date. | chain snapshot |
| Greeks | Delta, gamma, theta and vega for one option contract. | sensitivities |
| Implied volatility | The volatility that makes the option model price equal the market price. | IV |
| Strategy | The rule set that turns market data into signals. | algo, bot |
| Signal | An instruction from a strategy to enter or exit a position. | trigger |
| Screen | A run of a strategy's rules over the latest bars of a universe, which prints the symbols that qualify. | scan, screener, filter |
| Universe | The set of symbols a screen runs over. | watchlist, symbol list |
| Backtest | A run of a strategy over stored history, which produces simulated fills and one result. | backtest run, simulation |
| Paper trade | An order sent to a broker simulator instead of the market. | dry run, demo trade |
| Fill | The result of an order that traded, in whole or in part. | execution |
| Slippage | The difference between the price a backtest assumes and the price a fill gets. | market impact |
| Source | A provider of market data. | provider, vendor, feed |
| Dataset | The stored data that a screen or a backtest reads. One dataset can serve more than one run. | data set, cache |
| Point in time | A record is point in time when it holds only what was knowable at that moment. | as-of, look-ahead safe |

## Repository

| Word | Meaning | Do not use |
| --- | --- | --- |
| Feature | The top-level issue that says what to build. Issue #1 holds the trading lab. | map, epic, roadmap |
| Part | A child issue of the feature. It covers one piece of the build. | ticket, story, task |
| Note | A research finding stored in `docs/research/`. | report, write-up |
| Evidence | The facts in a note, kept separate from the decision they led to. | findings, data |
