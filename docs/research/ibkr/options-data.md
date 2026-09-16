# IBKR options data for backtesting

Status: research finding  
Evidence checked: 2026-09-16

## Scope

This note covers what Interactive Brokers supplies through its own APIs for options research: the TWS API (a socket into Trader Workstation or IB Gateway) and the Web API (also called the Client Portal API). It does not compare third-party historical option vendors. Every claim links to an IBKR page, fetched on 2026-09-16. Two claims come from IBKR's older TWS API site, which is still on IBKR's domain but shows a banner pointing to IBKR Campus; those are labelled deprecated. Where the current docs are silent on something the ticket asks about, I say so instead of guessing.

## Short answer

IBKR is built for live option trading, not for option backtesting. It will list the expirations and strikes that exist, stream quotes with greeks and implied volatility for a live contract, and return intraday bars for a contract while that contract is still alive. It will not return historical greeks, and it will not return anything for an expired option.

The retention gap is categorical, not just a shorter window. IBKR lists expired options, FOPs, warrants and structured products, and end-of-day data for the same, as unavailable historical data ([Unavailable Historical Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)). A backtest over option history therefore has to capture data forward, day by day, while the contracts trade, and store it locally. The docs do not describe a bulk historical option download.

Chain discovery is well covered on both APIs. Greeks and implied volatility are well covered live. Historical bars per contract exist but stop at expiry and have no end-of-day bars. Historical greeks do not exist at all.

## Chain discovery

The TWS API exposes `reqSecDefOptParams(reqId, underlyingSymbol, futFopExchange, underlyingSecType, underlyingConId)` ([Request Option Chains](https://ibkrcampus.com/docs/tws-api/doc/contracts-financial-instruments/option-chains/request-option-chains)). The callback `securityDefinitionOptionParameter` returns the underlying conId, trading class, multiplier, exchange, a set of expirations and a set of strikes ([Receive Option Chains](https://ibkrcampus.com/docs/tws-api/doc/contracts-financial-instruments/option-chains/receive-option-chains)). Passing an empty `futFopExchange` asks for all exchanges, and the callback fires once per exchange.

The response is a cross product. It returns every strike for the underlying and every expiration, not the list of contracts that actually exist. The options page states that some strike and expiry combinations do not produce a valid contract ([Options, deprecated](https://interactivebrokers.github.io/tws-api/options.html)). The response also carries no conId, no right, and no per-expiration expiry date beyond the strings in the expiration set.

The same deprecated page says `reqSecDefOptParams` does not carry the throttling that the older `reqContractDetails` chain method has, and that `reqContractDetails` on an incomplete option contract returns matching contracts but is throttled. The current docs give no call rate and no result cap for `reqSecDefOptParams` (see "What still needs checking").

The Web API covers the same ground in three calls ([Finding Options Chains](https://ibkrcampus.com/docs/web-api/trading/instrument-discovery/finding-options-chains)):

| Step | Endpoint | Returns |
| --- | --- | --- |
| 1 | `/iserver/secdef/search?symbol=...` | Underlying conId plus an OPT section with a semicolon-separated month list and exchanges |
| 2 | `/iserver/secdef/strikes?conid=...&sectype=OPT&month=...` | Separate call and put strike arrays for one month |
| 3 | `/iserver/secdef/info?conid=...&sectype=OPT&month=...&strike=...` | One record per matching contract: conid, right, strike, maturityDate, multiplier, tradingClass, validExchanges |

Step 3 needs one request per month and strike combination. IBKR's own article says the three calls must run in sequence "with no means around this process" and recommends running the chain build once in the morning at the start of a month rather than intraday ([Handling Options Chains](https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains), authored by IBKR's API Support Supervisor). The article is IBKR-authored but is a blog post, not reference documentation.

## Historical bars for one option contract

`reqHistoricalData` takes a contract, an end date and time, a duration string, a bar size, a `whatToShow` value, and an RTH flag ([Requesting Historical Bars](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars)). Duration units are seconds, days, weeks, months and years ([Duration](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/duration)).

| Bar size | Maximum duration in one request |
| --- | --- |
| 1 secs | 2000 S only, no day or larger |
| 5 secs to 1 day | 365 D, 52 W, 12 M or 68 Y |

The table above is the max duration per bar size page ([Max Duration Per Bar Size](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size)). Smaller durations allow a narrower band of bar sizes, for example a seconds duration allows 1 second to 1 minute bars and a year duration allows 1 minute to 1 day bars ([Step Sizes](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes)). `keepUpToDate` streams unfinished bars, and only for Trades, Midpoint, Bid and Ask ([Keep Up To Date](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/keep-up-to-date)).

Historical requests pace on three rules ([Pacing Violations for Small Bars](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less)):

- No identical historical request within 15 seconds.
- No six or more historical requests for the same contract, exchange and tick type within two seconds.
- No more than 60 requests in any ten minute period.

BID_ASK counts as two requests. IBKR states these limits apply to all clients and cannot be overcome.

The retention rules matter more than the pacing rules for backtesting. IBKR lists these as unavailable historical data ([Unavailable Historical Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)):

- Expired options, FOPs, warrants and structured products.
- End-of-day data for options, FOPs, warrants and structured products.
- Bars of 30 seconds or less that are older than six months.
- Time and Sales data beyond three years.

So an option contract that is still listed can be read, in intraday bar sizes, up to the limits above. Once it expires, the history is gone. IBKR does not document a retention number for live option intraday bars beyond the expiry rule.

Historical market data through the API needs a market data subscription. IBKR says the API "always requires Level 1 streaming real time data to return historical data", unlike the TWS charts which can show delayed data without a subscription ([Historical Market Data, deprecated](https://interactivebrokers.github.io/tws-api/historical_data.html)). The current docs say historical market data is available to subscribers ([Historical Market Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/introduction)) and that most securities need a Level 1 top-of-book subscription ([Market Data Subscriptions](https://ibkrcampus.com/docs/general/market-data-subscriptions/introduction)).

One helper call exists to ask where history starts. `reqHeadTimestamp(tickerId, contract, whatToShow, useRTH, formatDate)` returns the timestamp of the earliest available historical data for a contract and data type ([Requesting the Earliest Data Point](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/finding-the-earliest-available-data-point/requesting-the-earliest-data-point)).

## Tick-by-tick option data

`reqTickByTickData(reqId, contract, tickType, numberOfTicks, ignoreSize)` takes tick types "Last", "AllLast", "BidAsk" or "MidPoint". A non-zero `numberOfTicks` returns up to 1000 historical ticks first. The maximum simultaneous tick-by-tick subscriptions is 5% of the user's total market data lines ([Request Tick By Tick Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/tick-by-tick-data/request-tick-by-tick-data)).

The lines table makes that concrete. An account with 100 market data lines can hold 5 tick-by-tick subscriptions ([Specialized Market Data Lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines)).

The docs do not say that tick-by-tick is restricted by product, but they do warn that not all tick types are provided for all instruments at all times, and that the TWS API is only a delivery channel for what TWS already has ([Available Tick Types](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/available-tick-types/introduction), [Live Data Limitations](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/live-data-limitations)).

## Implied volatility and greeks

Live greeks come with the option quote. `reqMktData` on an option contract returns greeks automatically, and `tickOptionComputation` carries `impliedVolatility`, `delta`, `optPrice`, `pvDividend`, `gamma`, `vega`, `theta` and `undPrice` ([Request Options Greeks](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/request-options-greeks), [Receiving Options Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/receiving-options-data)). The `tickAttrib` field is 0 for return based and 1 for price based.

Four tick types deliver this ([Available Tick Types](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/available-tick-types/introduction)):

| Tick | Id | Basis |
| --- | --- | --- |
| Bid Option Computation | 10 | Option bid price and underlying price |
| Ask Option Computation | 11 | Option ask price and underlying price |
| Last Option Computation | 12 | Option last traded price and underlying price |
| Model Option Computation | 13 | Option model price; corresponds to the greeks shown in TWS, and also returns model implied volatility |

Delayed variants exist for users without live subscriptions as ticks 80 to 83, and tick 53 returns greeks for a user-supplied price. A market data subscription is needed for both the option and the underlying. IBKR states that a user without an underlying subscription gets a "Market Data Is Not Subscribed" error, which can be ignored if greeks are not wanted.

The API also computes on demand. `calculateImpliedVolatility` takes an option price and underlying price, and `calculateOptionPrice` takes a volatility and underlying price. Both return their result through `tickOptionComputation` ([Calculating option prices](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/calculating-option-prices), [Option Greeks, deprecated](https://interactivebrokers.github.io/tws-api/option_computations.html)).

At the underlying level, tick 24 gives the IB 30-day at-market implied volatility, built from option prices in two consecutive expiration months, and tick 23 gives a 30-day historical volatility for stocks ([Available Tick Types](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/available-tick-types/introduction)).

Historical greeks do not exist in the TWS API. The `whatToShow` values for historical bars include HISTORICAL_VOLATILITY and OPTION_IMPLIED_VOLATILITY, but both list their supported products as ETFs, indices and stocks, not options ([HISTORICAL_VOLATILITY](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/historical-volatility), [OPTION_IMPLIED_VOLATILITY](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/option-implied-volatility)). There is no greeks `whatToShow` value. Historical bars return open, high, low, close and volume only ([Historical Bar Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/introduction)).

The Web API has the same shape. Live snapshot fields include Delta (7308), Gamma (7309), Theta (7310), Vega (7311), Implied Vol. % (7633) for a specific option strike, Option Implied Vol. % (7283) for the underlying, and Hist. Vol. % (7087) ([Market Data Fields](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/market-data-fields)). The historical endpoint returns only open, close, high, low, volume and timestamp per bar, with a maximum of 1000 data points per request ([Historical Market Data](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/historical-market-data)).

The docs do not name the option model IBKR uses for its greeks.

## Pulling a chain without breaking limits

Market data lines cap how much can be alive at once. Accounts start with 100 concurrent real-time lines, shared between the TWS watchlist and every API connection. The allocation formula takes the greater of USD monthly commissions divided by 8, USD equity times 100 divided by 1,000,000 rounded down, and 100 ([How Market Data is Allocated](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated), [Market Data Lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/introduction)). Going over the cap returns an error asking for more lines.

Two ways to sample more contracts than the line cap allow:

- TWS API snapshots. `reqMktData` with the snapshot flag set returns the currently available data once, then `tickSnapshotEnd` fires about 11 seconds later. Snapshots only return default tick types; no generic ticks can be specified ([Streaming Data Snapshots](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/top-of-book-l-1/streaming-data-snapshots)).
- Web API snapshots. `/iserver/marketdata/snapshot` takes a comma-separated `conids` list, so many contracts go in one request ([Live Market Data Snapshot](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/live-market-data-snapshot), [Final Steps](https://ibkrcampus.com/docs/web-api/v1/endpoints/option-chains/final-steps)).

The Web API paces globally at 10 requests per second per authenticated username, with per-endpoint limits layered on. `/iserver/marketdata/snapshot` and `/iserver/marketdata/history` both allow 10 requests per second, and history also allows 50 per minute. A breach returns HTTP 429, and a violating IP can land in a 10 minute penalty box with repeat offenders blocked ([Pacing Limitations](https://ibkrcampus.com/docs/web-api/trading/usage-and-availability/pacing-limitations)). The `/iserver/secdef/*` endpoints used for chain discovery are not in the per-endpoint table, so only the global 10 per second rule is documented for them.

On the TWS API side, breaking pacing raises error 100, and three breaches terminate the API session with a broken pipe. The alternative setting lets TWS auto-pace requests instead of rejecting them ([Pacing Behavior](https://ibkrcampus.com/docs/tws-api/doc/pacing-limitations/pacing-behavior)).

Regulatory snapshots do not help here. They cover common US stocks only and are explicitly not available for ETFs, options or futures ([Regulatory Snapshots](https://ibkrcampus.com/docs/general/market-data-subscriptions/regulatory-snapshots)).

## Does one call serve live and backtest?

No. Live and historical are separate calls on both APIs.

| Need | TWS API | Web API |
| --- | --- | --- |
| Live quote, greeks, IV | `reqMktData`, `reqTickByTickData` | `/iserver/marketdata/snapshot` |
| Historical bars | `reqHistoricalData` | `/iserver/marketdata/history` |
| Chain definition | `reqSecDefOptParams` | `/iserver/secdef/search`, `/strikes`, `/info` |

The Web API snapshot endpoint also requires a prior call to `/iserver/accounts`, and for a derivative it requires `/iserver/secdef/search` first. The historical endpoint requires a conid.

The docs describe no bulk backfill and no historical chain snapshot. The only route to option history is to request bars per contract while it is live, or to record the live stream, and keep the result. IBKR's own chain article frames the same problem from the contract side, telling the developer to build the contract library ahead of time and reuse the conids, because the contract conId stays constant for the life of the option.

## Who owns the data, and can it be stored and reused

The docs do not say who owns the data or whether the user may store and redistribute it. What the docs do say points the other way:

- Market data is licensed. IBKR keeps 5% to 10% of market data fees to cover administration and pays the rest to the data vendor, and snapshot quotes carry additional fees ([Market Data Pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)).
- API data is treated as off-platform. IBKR states that free on-platform data in TWS is not the same as API data, because exchanges license off-platform viewing separately ([TWS Data vs API Data](https://ibkrcampus.com/docs/general/market-data-subscriptions/tws-data-vs-api-data)).
- Subscriptions are per user, and a live user may share data with exactly one paper user ([Market Data Sharing](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing)).
- API access needs a signed Market Data API Acknowledgement and an API usage questionnaire, including a disclosure of any automated system ([Market Data API Acknowledgement](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement), [Automation and Software Disclosure](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/api-user-activity-certification/automation-and-software-disclosure)).
- Users are classified as professional or non-professional, and everyone defaults to professional ([Professional vs Non-Professional](https://ibkrcampus.com/docs/general/market-data-subscriptions/professional-vs-non-professional)).

The actual terms live in account forms. IBKR lists "Market Data Agreements" with a downloadable sample GFIS Subscriber Agreement, but the document text is not on the documentation site ([Market Data Agreements](https://www.interactivebrokers.com/en/accounts/forms-and-disclosures-market-data.php)). Treat storage and reuse as a question for those terms and for exchange licensing, not something the API docs settle.

## Available from IBKR

| Item | Where | Notes |
| --- | --- | --- |
| Expirations and strikes per underlying and exchange | `reqSecDefOptParams`; `/iserver/secdef/search`, `/strikes` | Sets, not a validated contract list |
| Underlying conId, trading class, multiplier, exchange | `reqSecDefOptParams`; `/iserver/secdef/info` | Web API also returns contract conId, right and maturityDate |
| Intraday bars for a listed option | `reqHistoricalData` | 1 sec to 1 day bars, subject to step sizes |
| Historical tick data | `reqTickByTickData` with a count | Up to 1000 ticks first |
| Live option quote and greeks | `tickOptionComputation` ticks 10 to 13; Web API fields 7308 to 7311 | Subscription for option and underlying |
| Model implied volatility | Tick 13; Web API field 7633 | Live only |
| 30-day underlying IV and HV | Ticks 24, 23, 58 | Underlying level, live |
| On-demand IV or price calculation | `calculateImpliedVolatility`, `calculateOptionPrice` | Served through the same tick callback |
| Earliest available timestamp | `reqHeadTimestamp` | Per contract and data type |
| Chain build flow | Web API secdef endpoints | Sequential, one call per month and strike for conIds |

## Missing or undocumented

| Gap | Evidence |
| --- | --- |
| Historical data for expired options | Listed as unavailable |
| End-of-day bars for options | Listed as unavailable |
| Historical greeks per contract | No greeks `whatToShow`; historical bars return OHLCV only |
| Historical implied volatility per contract | OPTION_IMPLIED_VOLATILITY and HISTORICAL_VOLATILITY list ETFs, indices and stocks only |
| Bulk historical option download | Not documented on either API |
| Same call for live and backtest | Live and historical are separate calls on both APIs |
| A stored snapshot of a past chain | Not documented |
| Call rate or result cap for `reqSecDefOptParams` | Current docs are silent |
| Pacing limits specific to the secdef endpoints | Not in the Web API per-endpoint table |
| Retention number for live option intraday bars | Docs list categories, not durations |
| The option model behind IBKR greeks | Not named in the docs |
| Whether API data may be stored and reused | Not stated in the API docs |
| Exact tick-by-tick coverage for options | Docs only warn that not all tick types appear for all instruments |

## What still needs checking

- Ask IBKR API support for the documented cap, if any, on `reqSecDefOptParams` result size and call frequency, and for the pacing limits on `/iserver/secdef/search`, `/strikes` and `/info`.
- Confirm against a live paper account whether `reqHistoricalData` accepts an option conId, which `whatToShow` values it accepts, and how far back intraday option bars actually go. The docs imply this but do not state it.
- Measure how many option contracts a 100-line account can snapshot per minute through the Web API bulk snapshot before hitting 429, including the added cost of the secdef calls needed to learn the conIds.
- Check whether Web API `/iserver/marketdata/history` returns bars for option conids, and whether the greeks fields 7308 to 7311 populate for an option conid without an underlying subscription in practice.
- Read the GFIS Subscriber Agreement and the Market Data API Acknowledgement terms, and confirm whether storing API data locally for research and whether publishing derived results are permitted.
- Decide how much of this matters before choosing a data path. If the strategy needs historical greeks or expired contract history, IBKR cannot supply it and the deferred vendor comparison becomes the blocking decision.
