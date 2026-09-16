# IBKR historical market data limits and pacing

Status: research finding
Evidence checked: 2026-09-16

## Short answer

The TWS API returns bars by request, not as a live feed. You pick a bar size from 1 second to 1 month, a duration, and an `endDateTime`. One second bars cap at 2000 S in a single request. Bars from 5 seconds to 1 week share maxima of 86400 S, 365 D, 52 W, 12 M, or 68 Y. There is no paging API; move `endDateTime` backwards to page. [Max duration per bar size](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size)

Pacing bites first. No identical request within 15 seconds, fewer than six for the same contract, exchange, and tick type within two seconds, and no more than 60 in ten minutes. Three breaks can end the session. Intraday history is thin: bars of 30 seconds or less stop at six months, ticks at three years, and bond history at six months. Everything needs a Level 1 subscription on a funded IBKR Pro account, and a paper account only sees data the live account shares. [Pacing violations for small bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less) · [Unavailable historical data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)

The 2,000 bar cap repeated in forums is not on any current official page. The only official 2000 is the maximum second duration for 1 second bars.

## What will bite you

The 2,000 cap is unverified, and 86400 S of 5 second bars is 17,280 bars, which contradicts a hard 2,000 ceiling. Test it against a live account before you design around it. [Max duration per bar size](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size)

Pacing violations can end the session. The limits apply to all clients, cannot be overcome, and IBKR points heavy users at a specialist data vendor. Three breaks terminate the API session unless the TWS or IB Gateway setting is switched to queue and slow requests instead of rejecting them. Each Bid_Ask request counts twice. [Pacing violations for small bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less) · [Pacing behavior](https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/pacing-behavior)

Entitlement is a second gate. Using the TWS API at all needs a funded and opened IBKR Pro account. Market data through the API needs an opened IB account, since demo accounts cannot subscribe, plus IBKR Pro and USD 500 in the account on top of subscription cost. Funded status does not take effect until the next business day. Historical bars need a Level 1 streaming subscription, and most securities need a Level 1 top of book subscription, while forex and crypto do not. A paper account only sees data the live account shares, and only one paper account is allowed per live account. [Requirements](https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/requirements) · [Market data requirements](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-requirements) · [Minimum equity balance requirements](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-subscription-minimum-equity-balance-requirements) · [Market data subscriptions](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/introduction) · [Market data sharing](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing)

History is filtered, so it does not match what you see live. Daily volume from the unfiltered real time feed is generally larger than the filtered historical volume, and the same request at different times can return different data. Volume units also depend on a TWS setting: round lots if "Send market data in lots for US Stocks for dual-mode API clients" is checked, shares if not. [Historical data filtering](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/historical-data-filtering) · [Historical volume scaling](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/historical-volume-scaling)

Adjusted_Last adjusts for splits and dividends; plain Trades adjusts for splits only. A total return backtest on a stock or ETF probably wants Adjusted_Last. The docs do not state the adjustment formula, so treat the method as unverified. [TRADES](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/trades) · [ADJUSTED_LAST](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/adjusted-last)

The docs never say whether `endDateTime` is inclusive or how to overlap pages, so watch for duplicate or missing bars at page boundaries and reconcile them yourself. [Step sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes)

## Reference

### Request shape

Source for every row is [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) unless the row links elsewhere.

| Parameter | Rule |
| --- | --- |
| `endDateTime` | "YYYYMMDD HH:mm:ss TMZ", or empty for now. Must be empty for continuous futures. |
| `durationStr` | Amount to go back from `endDateTime`, in S, D, W, M, or Y ([Duration](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/duration)). |
| `barSizeSetting` | See bar sizes below ([Historical bar sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/historical-bar-sizes)). |
| `whatToShow` | Trades, Midpoint, Bid, Ask, Bid_Ask, Adjusted_Last, Historical_Volatility, Option_Implied_Volatility, Fee_Rate, the yield types, Schedule, AggTrades. |
| `useRTH` | 1 returns bars inside Regular Trading Hours only, 0 returns all hours available. |
| `formatDate` | 1 for a string time zone date, 2 for epoch, 3 for day and time. Day bars return yyyyMMdd only ([Format date received](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/format-date-received)). |
| `keepUpToDate` | Subscribes to updates of the unfinished bar and forbids `endDateTime`. Only Trades, Midpoint, Bid, and Ask. Updates arrive about every 4 to 6 seconds ([Keep up to date](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/keep-up-to-date)). |

A returned bar timestamp marks the start of the bar, not the end. A bar stamped 16:53:15 covers 16:53:15 to 16:53:20.

### Bar sizes

Source for both tables is [Historical bar sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/historical-bar-sizes) and [Step sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes).

| Unit | Sizes |
| --- | --- |
| secs | 1, 5, 10, 15, 30 |
| mins | 1, 2, 3, 5, 10, 15, 20, 30 |
| hours | 1, 2, 3, 4, 8 |
| day | 1 |
| weeks | 1 |
| months | 1 |

Not every size works with every duration.

| Duration unit | Bar units allowed | Bar size interval |
| --- | --- | --- |
| S | secs, mins | 1 secs to 1 min |
| D | secs, mins, hrs | 5 secs to 1 hour |
| W | secs, mins, hrs | 10 secs to 4 hrs |
| M | secs, mins, hrs | 30 secs to 8 hrs |
| Y | mins, hrs, d | 1 min to 1 day |

`reqRealTimeBars` is a separate 5 second stream of live data, not part of `reqHistoricalData`.

### Maximum lookback per single request

Source is [Max duration per bar size](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size). Every bar size from 5 secs to 1 week shares the same maxima.

| Bar size | Max second | Max day | Max week | Max month | Max year |
| --- | --- | --- | --- | --- | --- |
| 1 secs | 2000 S | Not supported | Not supported | Not supported | Not supported |
| 5 secs through 1 week | 86400 S | 365 D | 52 W | 12 M | 68 Y |

The page's own example: 5 second bars cap at 86400 S, so more than one day of 5 second bars needs requests in increments of D.

### Pacing

TWS API rules, from [Pacing violations for small bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less):

| Rule | Exact limit |
| --- | --- |
| Identical requests | Not within 15 seconds |
| Same contract, exchange, tick type | Fewer than six requests in two seconds |
| Total | No more than 60 requests in any ten minute period |
| Bid_Ask weighting | Each Bid_Ask request counts twice |

Over-limit requests are rejected, and three breaks end the session, unless the TWS or IB Gateway setting makes TWS queue and slow the client instead. [Pacing behavior](https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/pacing-behavior)

The Web API paces globally at 10 requests per second, plus per-endpoint limits. `/iserver/marketdata/history` allows 10 requests per second or 50 per minute, and returns a maximum of 1000 data points. Over-limit returns HTTP 429 and the IP enters a 15 minute penalty box, with repeat offenders permanently blocked. [Web API pacing limitations](https://ibkrcampus.com/docs/web-api/v1/pacing-limitations) · [Historical market data](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/historical-market-data)

### Market data lines

Every account starts with 100 concurrent real time lines, shared between TWS watchlists and API requests. After the first month the allowance is the greater of monthly USD commissions divided by 8, equity times 100 divided by 1,000,000 rounded down, or 100. The line count also sets the tick and depth caps: 100 lines allow 5 tick by tick streams and 3 simultaneous market depth symbols, and the values scale up from there. [Market data lines](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/introduction) · [How market data is allocated](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated) · [Specialized market data lines](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines)

### Historical ticks

Source is [Historical time and sales](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-time-sales/introduction) and [Requesting time and sales data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-time-sales/requesting-time-and-sales-data).

| Fact | Value |
| --- | --- |
| Function | `reqHistoricalTicks` |
| whatToShow | Bid_Ask, Midpoint, Trades |
| Max ticks per request | 1000 |
| Retention | Last 3 years only |
| Sessions | Data is not returned across multiple trading sessions in one request |
| Combos | Not available |
| Entitlement | Level 1 top of book, the same as `reqMktData` or `reqHistoricalData` |

### The historical farm and earliest data

Streaming requests use the market data farm and historical requests use the historical farm, with no documented automatic failover between them. In IB Gateway, "A historical data farm connection has become inactive but should be available upon demand" only means the farm went idle while no request was in flight; sending a request reconnects it. When a symbol has no historical data, the request fails instead of returning an empty bar set. [Market data farm connection is OK](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/common-error-resolution/market-data-farm-connection-is-ok)

`reqHeadTimestamp` finds the earliest available point for a contract and `whatToShow`, counts as an ongoing historical request, and must be cancelled with `cancelHeadTimeStamp`. [Finding the earliest data point](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/finding-the-earliest-available-data-point/introduction)

### Retention

Source is [Unavailable historical data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data).

| Data | Retention |
| --- | --- |
| Bars whose size is 30 seconds or less | Not available older than six months |
| Historical time and sales (ticks) | Last 3 years only |
| Expired futures | Two years from the future's expiration date |
| Expired options, FOPs, warrants, structured products | Not available |
| End of day data for options, FOPs, warrants, structured products | Not available |
| Bond data | Not available older than six months |
| Expired future spreads | Not available |
| Securities no longer trading | Not available |
| Native combo history | Not stored; a combo returns the sum of its legs |
| Symbol moved exchange | Usually unavailable before the move, including for SMART requests |
| Studies and indicators such as moving averages or Bollinger Bands | Not available from the API |

The 30 second rule shapes a backtest layer: 1 second, 5 second, 10 second, 15 second, and 30 second bars all fall off after six months, while 1 minute and above have no stated cutoff.

### Adjusted prices

| whatToShow | Adjustment | Supported products | Source |
| --- | --- | --- | --- |
| Trades | Adjusted for splits, not dividends | Bonds, ETFs, FOPs, Futures, Indices, Metals, Options, SSFs, Stocks, Structured Products, Warrants | [TRADES](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/trades) |
| Adjusted_Last | Adjusted for splits and dividends | ETFs, Options, Stocks | [ADJUSTED_LAST](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/adjusted-last) |
| AggTrades | Crypto only | Cryptocurrency | [AGGTRADES](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/aggtrades) |
