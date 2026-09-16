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
| Backtest | A run of a strategy over stored history, which produces simulated fills and one result. | backtest run, simulation |
| Paper trade | An order sent to a broker simulator instead of the market. | dry run, demo trade |
| Fill | The result of an order that traded, in whole or in part. | execution |
| Slippage | The difference between the price a backtest assumes and the price a fill gets. | market impact |
| Source | A provider of market data. | provider, vendor, feed |
| Dataset | The stored data that a backtest reads. One dataset can serve more than one backtest. | data set, cache |
| Point in time | A record is point in time when it holds only what was knowable at that moment. | as-of, look-ahead safe |

## Repository

| Word | Meaning | Do not use |
| --- | --- | --- |
| Map | The issue that holds the destination, the decisions and the open questions for one effort. | epic, roadmap |
| Destination | The end state that the map works toward. | goal, north star |
| Ticket | A child issue of the map that holds one question. | story, task |
| Decision ticket | A ticket that a human and an agent settle together. | grilling ticket |
| Research ticket | A ticket that an agent settles alone by reading primary sources. | spike |
| Claim | To assign a ticket to yourself before you work it. | pick up |
| Frontier | The open tickets that have no open blocker and no assignee. | backlog, queue |
| Not yet specified | Questions that are in scope but not clear enough to become a ticket. | fog, icebox |
| Out of scope | Work beyond the destination. It never becomes a ticket. | out of bounds |
