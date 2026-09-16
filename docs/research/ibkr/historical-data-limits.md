# IBKR historical market data limits and pacing

Status: research finding
Evidence checked: 2026-09-16

## Scope

I read the official Interactive Brokers documentation for the TWS API and the Web API v1, plus a few pages from the deprecated `interactivebrokers.github.io/tws-api` site because the current site drops some numbers those pages still state. I did not run an account against the API, so this note records what the docs promise, not what a live request returns. Where the pages disagree, I show both. Where a number is only a community claim, I say so.

The question is what a backtest data layer can pull, so I cover the request shape, the pacing rules, the retention rules, and the entitlement rules. I do not cover order handling.

## Short answer

The TWS API serves bars by request, not as a firehose. You pick a bar size (1 sec to 1 month), a duration string (S, D, W, M, Y), and an `endDateTime`, and you get back a bounded window. The largest documented windows are 1 second bars limited to 2000 S in one request and 5 second to 1 week bars with maxima of 86400 S, 365 D, 52 W, 12 M, or 68 Y per request. There is no paging API; you page by moving `endDateTime` backwards, and the docs do not spell out a paging recipe.

The 2,000 bar cap that gets repeated everywhere is not stated as a general rule on any current official page I could find. The only official 2000 is the max second-duration for 1 second bars. The current docs instead say requests must be assembled so that "only a few thousand bars are returned at a time". Treat the 2,000 figure as unverified.

Pacing is the real constraint. Identical requests inside 15 seconds, six or more requests for the same contract, exchange, and tick type inside two seconds, or more than 60 requests in any ten minutes is a violation. Repeat violations can end the API session. Intraday depth is thin: bars 30 seconds or less stop at six months, historical ticks stop at three years, and bond history stops at six months. Everything above needs a Level 1 subscription on a funded IBKR Pro account, and a paper account only sees data if the live account shares it.

## Historical bar requests (TWS API `reqHistoricalData`)

| Parameter | Rule | Source |
| --- | --- | --- |
| `endDateTime` | "YYYYMMDD HH:mm:ss TMZ" or empty string for now. Must be empty for continuous futures. | [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) |
| `durationStr` | Amount to go back from `endDateTime`. Units are S, D, W, M, Y. | [Duration](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/duration) |
| `barSizeSetting` | See the bar size table below. | [Historical bar sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/historical-bar-sizes) |
| `whatToShow` | Trades, Midpoint, Bid, Ask, Bid_Ask, Adjusted_Last, Historical_Volatility, Option_Implied_Volatility, Fee_Rate, the yield types, Schedule, AggTrades. | [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) |
| `useRTH` | Bool. 1 returns bars inside Regular Trading Hours only, 0 returns all hours available. | [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) |
| `formatDate` | 1 = string time zone date, 2 = epoch, 3 = day and time. Day bars only return yyyyMMdd. | [Format date received](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/format-date-received) |
| `keepUpToDate` | Bool. True subscribes to updates of the unfinished bar and forbids `endDateTime`. Supported only for Trades, Midpoint, Bid, Ask. Updates arrive about every 4 to 6 seconds. | [Keep up to date](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/keep-up-to-date) and [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) |
| `chartOptions` | Internal use only. | [Requesting historical bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) |

The returned bar timestamp marks the start of the bar, not the end. A bar stamped 16:53:15 covers 16:53:15 to 16:53:20.

## Bar sizes

Valid sizes, from [Historical bar sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/historical-bar-sizes):

| Unit | Sizes |
| --- | --- |
| secs | 1, 5, 10, 15, 30 |
| mins | 1, 2, 3, 5, 10, 15, 20, 30 |
| hours | 1, 2, 3, 4, 8 |
| day | 1 |
| weeks | 1 |
| months | 1 |

Smallest size is 1 second. TWS also has a separate 5 second real time bar stream (`reqRealTimeBars`), which is live data, not part of `reqHistoricalData`.

Not every size works with every duration. The [Step sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes) page gives the allowed min and max bar for each duration unit:

| Duration unit | Bar units allowed | Bar size interval |
| --- | --- | --- |
| S | secs, mins | 1 secs to 1 min |
| D | secs, mins, hrs | 5 secs to 1 hour |
| W | secs, mins, hrs | 10 secs to 4 hrs |
| M | secs, mins, hrs | 30 secs to 8 hrs |
| Y | mins, hrs, d | 1 min to 1 day |

## Maximum lookback per single request

From [Max duration per bar size](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size). Every bar size from 5 secs to 1 week shares the same maxima, so I list it once.

| Bar size | Max second duration | Max day duration | Max week duration | Max month duration | Max year duration |
| --- | --- | --- | --- | --- | --- |
| 1 secs | 2000 S | Not supported | Not supported | Not supported | Not supported |
| 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1M, 1W | 86400 S | 365 D | 52 W | 12 M | 68 Y |

The page's own example: 5 second bars cap at 86400 S, so more than one day of 5 second bars needs requests in increments of D. Note that 86400 S of 5 second bars is 17,280 bars, which is far above a 2,000 bar ceiling. That is one reason I do not treat the 2,000 bar claim as a documented cap.

## The 2,000 bar cap and other per-request caps

I could not find a general 2,000 bar cap on any current official page. Here is what the docs actually say.

| Claim | What the current docs say | Source |
| --- | --- | --- |
| 2,000 bars maximum per request | Not stated as a general rule. The value 2000 appears only as the max second-duration for 1 second bars. The [Step sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes) page says requests "need to be assembled in such a way that only a few thousand bars are returned at a time". | [Step sizes](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/step-sizes), [Max duration per bar size](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bars/max-duration-per-bar-size) |
| Maximum simultaneous historical requests | 50, stated only on the deprecated site. The current site does not repeat it. | [Deprecated historical data limitations](https://interactivebrokers.github.io/tws-api/historical_limitations.html) |
| Web API `/iserver/marketdata/history` row cap | "This endpoint provides a maximum of 1000 data points." | [Web API historical market data](https://ibkrcampus.com/docs/web-api/v1/endpoints/market-data/historical-market-data) |
| Historical tick cap | Max 1000 ticks per request. | [Requesting time and sales data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-time-sales/requesting-time-and-sales-data) |

Community sources repeat a 2,000 bar cap. A 2017 StackOverflow answer says "estimate 2000 bars", and a twsapi groups.io thread says a request "always returns the most recent 2000 bars". Those are not official and contradict the documented 86400 S window for 5 second bars, so I am not recording 2000 as a limit. I am recording it as unresolved.

The deprecated docs add a footnote worth knowing: for barSize 1 min and greater the hard limit was lifted, but IB still applies a "soft" throttle to balance load, and "requesting too much historical data can lead to throttling and eventual disconnect". That page is deprecated, so treat it as historical context.

## Paging backwards

The docs do not describe a paging procedure. The only mechanism is `endDateTime`: set it to the earliest timestamp you already hold and request again. The docs never show a worked paging example, never say whether `endDateTime` is inclusive, and never specify an overlap rule. That gap is on the "what still needs checking" list.

`reqHeadTimestamp` finds the earliest available point for a contract and `whatToShow`. It counts as an ongoing historical request, follows the 30 second bar limitations, and must be cancelled with `cancelHeadTimeStamp`. See [Finding the earliest data point](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/finding-the-earliest-available-data-point/introduction).

## Pacing rules (TWS API)

From [Pacing violations for small bars](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/pacing-violations-for-small-bars-30-secs-or-less):

| Rule | Exact limit |
| --- | --- |
| Identical requests | Not within 15 seconds |
| Same contract, exchange, tick type | Fewer than six requests in two seconds |
| Total | No more than 60 requests in any ten minute period |
| Bid_Ask weighting | Each Bid_Ask request counts twice |

The page says these limits apply to all clients and cannot be overcome, and points heavy users at a specialist data vendor.

The penalty is in [Pacing behavior](https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/pacing-behavior), which is a TWS or IB Gateway setting:

| Setting | Behavior |
| --- | --- |
| "Reject messages above maximum allowed message rate vs applying pacing" checked | TWS sends error code 100. After three pacing breaks the API session terminates, surfacing as WinError 10053 on Windows or a BrokenPipe error on MacOS and Linux. |
| Unchecked | TWS queues requests and waits in the EReader thread before moving on, so the client is slowed instead of cut off. |

Error 100 is also listed against the separate 50 messages per second message-rate limit, so the code alone does not tell you which limit broke. See [Error codes](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes).

The Web API has its own pacing, from [Web API pacing limitations](https://ibkrcampus.com/docs/web-api/v1/pacing-limitations): a global 10 requests per second, plus per-endpoint limits. `/iserver/marketdata/history` is 10 requests per second or 50 per minute. Over-limit returns HTTP 429, and the IP goes into a 15 minute penalty box. Repeat offenders can be permanently blocked.

## Market data lines

From [Market data lines](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/introduction) and [How market data is allocated](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated):

| Fact | Value |
| --- | --- |
| Initial concurrent real time lines | 100 |
| Minimum | 100 |
| Allocation after the first month | Greater of monthly USD commissions divided by 8, equity times 100 divided by 1,000,000 rounded down, or 100 |

Lines cover TWS watchlists and API requests together. The docs define a line as an active real time top-of-book request and are silent on whether a historical bar request consumes one. The line count also sets the tick and depth limits, from [Specialized market data lines](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines):

| Market data lines | Tick by tick streams | Max market depth |
| --- | --- | --- |
| 100 | 5 | 3 |
| 101 to 200 | 10 | 3 |
| 201 to 300 | 15 | 3 |
| 301 to 400 | 20 | 3 |
| 401 to 500 | 25 | 4 |
| 501 to 600 | 30 | 5 |
| 601 to 700 | 35 | 6 |
| 701 to 800 | 40 | 7 |
| 801 to 900 | 45 | 8 |
| 901 to 1000 | 50 | 9 |
| 1001 to 1100 | 55 | 10 |
| 1100+ | 60 to 500 | 11 to 60 |

The page notes tick lines scale at roughly 5 percent of total lines and calls the values approximations.

## HMDS versus live data

Historical requests and streaming requests go to different farms, and the docs only partly describe the switch.

| Fact | Source |
| --- | --- |
| Error and warning codes 2104, 2106, and 2158 mean a farm connection is OK and the API reached IBKR. 2106 is specifically "A historical data farm is connected". | [Market data farm connection is OK](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/common-error-resolution/market-data-farm-connection-is-ok), [Error codes](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes) |
| In IB Gateway the message "A historical data farm connection has become inactive but should be available upon demand" means the historical farm went idle while no historical request was in flight. Sending a historical request reconnects the farm. | [Market data farm connection is OK](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/common-error-resolution/market-data-farm-connection-is-ok) |
| Historical bars require a streaming Level 1 subscription. The deprecated page puts it plainly: "the API always requires Level 1 streaming real time data to return historical data". | [Deprecated historical market data](https://interactivebrokers.github.io/tws-api/historical_data.html) |
| The current general rule is that most securities need a Level 1 top of book subscription to get market data through the API. Forex and crypto do not. | [Market data subscriptions](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/introduction) |

The docs do not describe an automatic failover from live data to historical data, or the reverse. The farm in use follows the request type: streaming requests use the market data farm, historical requests use the historical farm.

When a symbol has no historical data, the request fails rather than returning an empty bar set. The relevant responses are error 165, "Historical market Data Service query message", described as "no such data in IB's database"; error 162, "Historical market data Service error message", which is also used for HMDS messages such as "HMDS query returned no data"; and error 166, "HMDS Expired Contract Violation". Sources: [Error codes](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes) and the deprecated [third party FAQ](https://interactivebrokers.github.io/tws-api/third_party.html). The deprecated FAQ also notes that a request for a date before a symbol started quoting returns "HMDS query returned no data".

## Historical tick data

From [Historical time and sales](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-time-sales/introduction) and [Requesting time and sales data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-time-sales/requesting-time-and-sales-data):

| Fact | Value |
| --- | --- |
| Function | `reqHistoricalTicks` |
| whatToShow | Bid_Ask, Midpoint, Trades |
| Max ticks per request | 1000 |
| Retention | Last 3 years only |
| Sessions | Data is not returned across multiple trading sessions in one request, so a spanning query needs several requests |
| Combos | Not available |
| Odd behavior | To complete a full second, more ticks may be returned than requested |
| Entitlement | Level 1 top of book subscription, the same as `reqMktData` or `reqHistoricalData` |
| Streaming tick limit | 5 concurrent streams at 100 market data lines, per the specialized lines table |

`ignoreSize` drops updates that change only size, not price, for Bid_Ask requests. Options and future options return size 1 unless a bid or ask was removed, in which case price and size are 0.

## Paper account versus funded account

| Fact | Source |
| --- | --- |
| In order to use the TWS API at all: a funded and opened IBKR Pro account. | [Requirements](https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/requirements) |
| To get market data through the API: an opened IB account (demo accounts cannot subscribe), IBKR Pro type, and USD 500 in the account on top of subscription cost. | [Market data requirements](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-requirements) |
| The USD 500 minimum is the individual and institutional figure. A funded status does not take effect until the next business day, so subscriptions added the same day are not available until then. | [Minimum equity balance requirements](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-subscription-minimum-equity-balance-requirements) |
| A paper account can share the live account's market data subscription. One paper account per live account. | [Market data sharing](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing) |
| The deprecated sharing rule is stricter: the paper user gets live data only if the live user is not logged in on a different computer at the same time. | [Deprecated streaming market data](https://interactivebrokers.github.io/tws-api/market_data.html) |
| Paper accounts simulate fills from the top of the book with no deep book access, and the simulator relies on more simulated technology than live. | [Paper trading](https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/limitations/paper-trading), [About paper trading accounts](https://www.ibkrguides.com/clientportal/aboutpapertradingaccounts.htm) |
| Deprecated FAQ: "it is not possible to receive real time market data or historical candlesticks for most instruments from the TWS API with a trial account login." | [Deprecated third party FAQ](https://interactivebrokers.github.io/tws-api/third_party.html) |

The docs are silent on whether a fully funded live account with no subscription can pull delayed bars through the API. They only say delayed data must be requested explicitly with `reqMarketDataType(3)` and that subscriptions still gate most API data. See [Market data type behavior](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-delayed/market-data-type-behavior).

## Retention rules

From [Unavailable historical data](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data). These are the exact retention rules the docs give, and intraday is definitely shorter than daily.

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

The 30 second rule is the one that shapes a backtest layer: 1 second, 5 second, 10 second, 15 second, and 30 second bars all fall off after six months, while 1 minute and above do not have a stated cutoff.

## Adjusted prices

| whatToShow | Adjustment | Supported products | Source |
| --- | --- | --- | --- |
| Trades | Adjusted for splits, not dividends | Bonds, ETFs, FOPs, Futures, Indices, Metals, Options, SSFs, Stocks, Structured Products, Warrants | [TRADES](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/trades) |
| Adjusted_Last | Adjusted for splits and dividends | ETFs, Options, Stocks | [ADJUSTED_LAST](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/adjusted-last) |
| AggTrades | Crypto only | Cryptocurrency | [AGGTRADES](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-bar-what-to-show/aggtrades) |

You do not have to use `Adjusted_Last`, but if you backtest total return on a stock or ETF you probably want it, because plain Trades prices jump on splits and ignore dividends. The docs do not state the adjustment formula, do not say whether the adjustment uses the current share count or a point in time count, and do not say whether `Adjusted_Last` can go negative for very old data. Treat the adjustment method as unverified.

Two more data quality facts matter for a backtest layer. Historical data is filtered, so the volume and VWAP differ from the live feed: "the daily volume from the (unfiltered) real time data functionality will generally be larger than the (filtered) historical volume". And because IB adjusts, compresses, and filters history, "there may be historical data differences if you request historical data at different time points". Sources: [Historical data filtering](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/historical-data-filtering), [Deprecated historical market data](https://interactivebrokers.github.io/tws-api/historical_data.html).

Volume units depend on a TWS setting. If "Send market data in lots for US Stocks for dual-mode API clients" is checked, historical volume returns as round lots; unchecked, it returns in shares. See [Historical volume scaling](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/historical-volume-scaling).

## What still needs checking

- The general 2,000 bar cap. No current official page states it. The community claim is 2,000 and it is repeated in old forum posts and StackOverflow, but the documented 86400 S window for 5 second bars disproves it as a hard rule. A live account would settle it.
- Paging semantics. The docs never say whether `endDateTime` is inclusive, how to overlap pages, or how to avoid duplicate or missing bars at page boundaries.
- Whether `useRTH` boundaries are the exchange session or a fixed 09:30 to 16:00. The docs only say "Regular Trading Hours" without defining the session per exchange.
- The `Adjusted_Last` formula and whether adjusted prices can go negative. The docs only say "adjusted for splits and dividends".
- Whether a funded account with no subscription can pull delayed bars through the API, and how many bars delayed history returns.
- What `/hmds/history` (the beta endpoint referenced in an IBKR Campus lesson) returns. Its row cap and period limits are not in the reference docs; only `/iserver/marketdata/history` is documented, and its cap is 1000 points.
- The current status of the "50 simultaneous historical requests" limit. It appears only on the deprecated site.
- Whether the 30 second bar pacing rules still cause a temporary ban, or only session termination after three error 100 events. The docs describe session termination, not a timed account ban.
- Real behavior of the historical farm reconnect. The docs say it reconnects on demand, but not how long the first request waits.
- The exact number of data points a default 100 line paper account can pull before throttling. The line table is about live streams, and the pacing rules are about request rate, but the docs do not join the two.
