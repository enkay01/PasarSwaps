# IBKR options data for backtesting

Status: research finding
Evidence checked: 2026-09-16

## What you can get

Interactive Brokers will not give you option history. It lists expired options, FOPs, warrants and structured products, and end-of-day data for the same, as unavailable historical data. Once a contract expires, its record is gone, and the docs describe no bulk historical option download. [Unavailable Historical Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)

Historical greeks do not exist either. `reqHistoricalData` returns open, high, low, close and volume only ([Historical Bar Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/introduction)). The two volatility series it does offer, HISTORICAL_VOLATILITY and OPTION_IMPLIED_VOLATILITY, list ETFs, indices and stocks as their supported products, not options ([HISTORICAL_VOLATILITY](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/historical-volatility), [OPTION_IMPLIED_VOLATILITY](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/option-implied-volatility)). There is no greeks `whatToShow` value.

The live side works. Both APIs list the expirations and strikes that exist, and a live option quote comes with implied volatility and greeks attached. Option history therefore has to be captured forward: record the live stream, or pull bars per contract while it is still listed, and keep the result. The contract conId stays constant for the life of the option, so a library of conIds can be built once and reused. [Handling Options Chains](https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains)

## Chain discovery

The TWS API call is `reqSecDefOptParams(reqId, underlyingSymbol, futFopExchange, underlyingSecType, underlyingConId)` ([Request Option Chains](https://ibkrcampus.com/docs/tws-api/doc/contracts-financial-instruments/option-chains/request-option-chains)). The `securityDefinitionOptionParameter` callback returns the underlying conId, trading class, multiplier, exchange, and sets of expirations and strikes ([Receive Option Chains](https://ibkrcampus.com/docs/tws-api/doc/contracts-financial-instruments/option-chains/receive-option-chains)). An empty `futFopExchange` asks all exchanges, and the callback fires once per exchange. The response is a cross product: every strike against every expiration, not the contracts that actually exist, and some combinations produce no valid contract ([Options, deprecated](https://interactivebrokers.github.io/tws-api/options.html)). It carries no conId, no right and no per-expiration expiry date.

The Web API builds the same chain in three sequential calls ([Finding Options Chains](https://ibkrcampus.com/docs/web-api/trading/instrument-discovery/finding-options-chains)):

| Step | Endpoint | Returns |
| --- | --- | --- |
| 1 | `/iserver/secdef/search?symbol=...` | Underlying conId plus an OPT section with a semicolon-separated month list and exchanges |
| 2 | `/iserver/secdef/strikes?conid=...&sectype=OPT&month=...` | Separate call and put strike arrays for one month |
| 3 | `/iserver/secdef/info?conid=...&sectype=OPT&month=...&strike=...` | One record per matching contract: conid, right, strike, maturityDate, multiplier, tradingClass, validExchanges |

Step 3 takes one request per month and strike. IBKR's own article says the calls must run in sequence with no way around it, and recommends building the chain once in the morning at the start of a month. [Handling Options Chains](https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains)

## Live greeks and implied volatility

`reqMktData` on an option returns greeks automatically through `tickOptionComputation`, which carries `impliedVolatility`, `delta`, `optPrice`, `pvDividend`, `gamma`, `vega`, `theta` and `undPrice` ([Request Options Greeks](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/request-options-greeks), [Receiving Options Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/receiving-options-data)). `tickAttrib` is 0 for return based and 1 for price based.

| Tick | Id | Basis |
| --- | --- | --- |
| Bid Option Computation | 10 | Option bid price and underlying price |
| Ask Option Computation | 11 | Option ask price and underlying price |
| Last Option Computation | 12 | Option last traded price and underlying price |
| Model Option Computation | 13 | Option model price, matching the greeks shown in TWS, and the model implied volatility |

Delayed variants are ticks 80 to 83, and tick 53 returns greeks for a price you supply. Both the option and the underlying need a market data subscription. Without the underlying subscription IBKR returns a "Market Data Is Not Subscribed" error, which can be ignored if greeks are not wanted. [Available Tick Types](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/available-tick-types/introduction)

`calculateImpliedVolatility` takes an option price and an underlying price, `calculateOptionPrice` takes a volatility and an underlying price, and both answer through `tickOptionComputation` ([Calculating option prices](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/option-greeks/calculating-option-prices), [Option Greeks, deprecated](https://interactivebrokers.github.io/tws-api/option_computations.html)). At the underlying level, tick 24 gives the IB 30-day at-market implied volatility built from option prices in two consecutive expiration months, and tick 23 gives 30-day historical volatility for stocks. [Available Tick Types](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/available-tick-types/introduction)

On the Web API the live snapshot fields are Delta (7308), Gamma (7309), Theta (7310), Vega (7311) and Implied Vol. % (7633) for a strike, plus Option Implied Vol. % (7283) and Hist. Vol. % (7087) for the underlying ([Market Data Fields](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/market-data-fields)). The historical endpoint returns open, close, high, low, volume and timestamp per bar, up to 1000 points per request ([Historical Market Data](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/historical-market-data)).

## Capturing history forward

Per-contract bars come from `reqHistoricalData`, which takes a contract, an end time, a duration, a bar size, a `whatToShow` value and an RTH flag ([Requesting Historical Bars](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars)). Duration units are seconds, days, weeks, months and years ([Duration](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/duration)). A 1 second bar allows only a 2000 second duration; 5 seconds through 1 day allows up to 365 days, 52 weeks, 12 months or 68 years, and the duration also narrows which bar sizes are allowed, so a year allows 1 minute to 1 day bars ([Max Duration Per Bar Size](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size), [Step Sizes](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes)). `keepUpToDate` streams unfinished bars for Trades, Midpoint, Bid and Ask only ([Keep Up To Date](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/keep-up-to-date)). `reqHeadTimestamp` returns the earliest available timestamp for a contract and data type ([Requesting the Earliest Data Point](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/finding-the-earliest-available-data-point/requesting-the-earliest-data-point)).

Fine bars expire faster than the contract does. IBKR lists bars of 30 seconds or less as unavailable beyond six months and time and sales beyond three years, so intraday option bars have to be captured while they are still served ([Unavailable Historical Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)).

Historical data through the API needs a market data subscription. IBKR says the API "always requires Level 1 streaming real time data to return historical data", unlike TWS charts, which can show delayed data without a subscription ([Historical Market Data, deprecated](https://interactivebrokers.github.io/tws-api/historical_data.html)). The current docs say historical market data is available to subscribers ([Historical Market Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/introduction)).

Do not repeat an identical historical request within 15 seconds, and do not send six or more requests for the same contract, exchange and tick type within two seconds. The cap is 60 requests in any ten minutes, and BID_ASK counts as two. IBKR states the limits apply to all clients and cannot be overcome. [Pacing Violations for Small Bars](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less)

Market data lines cap how much can be alive at once. Accounts start with 100 concurrent real-time lines, shared between the TWS watchlist and every API connection, and the allowance is the greater of monthly USD commissions divided by 8, USD equity times 100 divided by 1,000,000, or 100 ([How Market Data is Allocated](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated), [Market Data Lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/introduction)). Going over the cap returns an error asking for more lines. To sample more contracts than the cap allows, request a TWS API snapshot with the snapshot flag, which returns data once, fires `tickSnapshotEnd` about 11 seconds later and only returns default tick types ([Streaming Data Snapshots](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/top-of-book-l-1/streaming-data-snapshots)), or send a comma-separated `conids` list to `/iserver/marketdata/snapshot` ([Live Market Data Snapshot](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/live-market-data-snapshot)). Tick-by-tick subscriptions are capped at 5% of the line count, so 5 on a 100-line account ([Request Tick By Tick Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/tick-by-tick-data/request-tick-by-tick-data), [Specialized Market Data Lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines)).

The Web API paces at 10 requests per second per authenticated username, with per-endpoint limits on top. Snapshot and history both allow 10 per second, and history also allows 50 per minute. A breach returns HTTP 429, and a violating IP can land in a 10 minute penalty box. The `/iserver/secdef/*` endpoints are not in the per-endpoint table, so only the global rule is documented for them. [Pacing Limitations](https://ibkrcampus.com/docs/web-api/trading/usage-and-availability/pacing-limitations) On the TWS API side, breaking pacing raises error 100, and three breaches terminate the session with a broken pipe, while an alternative setting lets TWS pace requests instead of rejecting them. [Pacing Behavior](https://ibkrcampus.com/docs/tws-api/doc/pacing-limitations/pacing-behavior)

## Reference detail

Live and historical are separate calls on both APIs. A Web API snapshot needs a prior `/iserver/accounts` call, and for a derivative a `/iserver/secdef/search` call first, and the historical endpoint needs a conid. [Live Market Data Snapshot](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/live-market-data-snapshot), [Historical Market Data](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/historical-market-data)

Regulatory snapshots do not help with options. They cover common US stocks only and are not available for ETFs, options or futures. [Regulatory Snapshots](https://ibkrcampus.com/docs/general/market-data-subscriptions/regulatory-snapshots)

The docs do not say whether API data may be stored or reused. What they do say points elsewhere. Market data is licensed, with IBKR keeping 5% to 10% of market data fees to cover administration and paying the rest to the data vendor ([Market Data Pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)). Free on-platform data in TWS is not the same as API data, because exchanges license off-platform viewing separately ([TWS Data vs API Data](https://ibkrcampus.com/docs/general/market-data-subscriptions/tws-data-vs-api-data)). Subscriptions are per user, and a live user may share data with exactly one paper user ([Market Data Sharing](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing)). API access needs a signed Market Data API Acknowledgement and an API usage questionnaire that discloses any automated system ([Market Data API Acknowledgement](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement), [Automation and Software Disclosure](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/api-user-activity-certification/automation-and-software-disclosure)). The actual terms sit in the account forms, where IBKR lists Market Data Agreements with a downloadable sample GFIS Subscriber Agreement but does not publish the text on the documentation site ([Market Data Agreements](https://www.interactivebrokers.com/en/accounts/forms-and-disclosures-market-data.php)).

| Gap | Evidence |
| --- | --- |
| Historical data for expired options | Listed as unavailable |
| End-of-day bars for options | Listed as unavailable |
| Historical greeks per contract | No greeks `whatToShow`; historical bars return OHLCV only |
| Historical implied volatility per contract | The volatility `whatToShow` values list ETFs, indices and stocks only |
| Bulk historical option download | Not documented on either API |
| Stored snapshot of a past chain | Not documented on either API |
