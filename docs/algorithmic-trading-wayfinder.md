# Algorithmic trading research map

Status: research only. This file is the reading index. Decisions and open tickets live on the [issue map](https://github.com/enkay01/PasarSwaps/issues/1).

## Where this stands

Interactive Brokers is the broker, chosen on 2026-09-16. The first round of research then showed that the broker is also the hard part. A paper account needs a funded live account before it exists. The API needs a gateway process with a browser login and a weekly re-authentication. Expired option contracts have no history at all, and historical Greeks do not exist. Request pacing is tight enough that pulling a few years of data takes planning.

That is more machinery than a hobby project needs, which is what the second round is for. Three research tickets are open on the cheap and easy path, and a fourth picks the stack once they land.

## Round one notes

[IBKR API options](research/ibkr/api-surfaces.md) covers the three ways to connect. IB Gateway is the lightest of them. Neither gateway nor Trader Workstation runs headless, and the API cannot tell a paper account from a live one.

[IBKR historical data limits](research/ibkr/historical-data-limits.md) covers bar sizes, how far back one request reaches, request pacing, and which data ages out.

[IBKR market data subscriptions](research/ibkr/market-data-subscriptions.md) covers what must be paid before any data flows, and what a US stock and options feed costs.

[IBKR options data](research/ibkr/options-data.md) covers chain discovery and live Greeks, and the gap that matters: no history for expired contracts.

Three older notes cover [hobby projects](research/hobby-algorithmic-trading-builds.md), [Massive request limits](research/massive-rate-limits-and-batching.md), and [institutional options vendors](research/credit-spreads/historical-options-and-event-data.md).

## Open tickets

| Ticket | Type | Question |
| --- | --- | --- |
| [#17](https://github.com/enkay01/PasarSwaps/issues/17) | research | Where a hobbyist gets options data |
| [#18](https://github.com/enkay01/PasarSwaps/issues/18) | research | Where a hobbyist gets market data |
| [#19](https://github.com/enkay01/PasarSwaps/issues/19) | research | The easiest paper trading and backtesting path |
| [#20](https://github.com/enkay01/PasarSwaps/issues/20) | decision | Pick the hobbyist stack |
| [#16](https://github.com/enkay01/PasarSwaps/issues/16) | decision | Choose the IBKR API surface |
| [#15](https://github.com/enkay01/PasarSwaps/issues/15) | decision | The contract a data source must satisfy so one acquisition serves many backtests |

## Adding a note

Write the claim, the source link, the date checked, and what is still unknown. Follow `AGENTS.md`. Keep a product decision separate from the evidence behind it, and put the decision on the issue map rather than here.
