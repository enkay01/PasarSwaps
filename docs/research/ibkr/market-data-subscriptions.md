# IBKR market data subscriptions and permissions

Status: research finding
Evidence checked: 2026-09-16

## What to do

Open an approved and funded live account on the IBKR Pro tier, and leave at least USD 500 of equity beyond the cost of the subscriptions. Demo accounts cannot subscribe to data. Sign the Market Data API Acknowledgement, because without it API requests come back saying the market data is not subscribed.

Change your subscriber status to non-professional in Client Portal before you buy. IBKR classifies every user as professional by default, and that status multiplies some of the prices below.

Then buy the US Equity and Options Add-On Streaming Bundle for API streaming, plus OPRA for option quotes. The free real-time stream from Cboe One and IEX is non-consolidated and does not show the NBBO, so add the network subscriptions if you need a consolidated quote. An option chain needs no subscription per underlying, but the underlying price comes from the equity subscription for that symbol, and IBKR says Greeks need a subscription for both the underlying and the derivative.

Sources: [market data requirements](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-requirements) · [Market Data API Acknowledgement](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement) · [professional vs non-professional](https://ibkrcampus.com/docs/general/market-data-subscriptions/professional-vs-non-professional) · [understanding market data subscriptions](https://ibkrcampus.com/docs/general/market-data-subscriptions/understanding-market-data-subscriptions)

## What to buy

Prices checked 2026-09-16, in USD per month. The source for every row is the [market data pricing page](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php).

| Subscription | Non-professional | Professional | Notes |
| --- | --- | --- | --- |
| US Real-Time Non-Consolidated Streaming Quotes | Free | Free | Cboe One and IEX, no NBBO |
| US Securities Snapshot and Futures Value Bundle | 10.00 base plus 0.01 per snapshot | not offered | Non-professional product. Base waived at USD 30.00 monthly commissions. The streaming bundle requires it as its base |
| US Equity and Options Add-On Streaming Bundle | 4.50 | 125.00 | Adds API streaming for equities and options. Waived above USD 5.00 non-professional and USD 15.00 professional commissions |
| OPRA (US Option Exchanges) (L1) | 1.50 | 32.75 | All US options in one product. Waived for all users at USD 20.00 monthly commissions |
| NYSE (Network A/CTA) (L1) | 1.50 | 45.00 | NYSE listed |
| NYSE American, BATS, ARCA, IEX and Regional Exchanges (Network B) (L1) | 1.50 | 25.00 | ARCA, AMEX, BATS, IEX and regionals |
| NASDAQ (Network C/UTP) (L1) | 1.50 | 25.00 | NASDAQ listed |
| Quote Booster pack | 30.00 per pack | 30.00 per pack | Adds 100 Level 1 quotes and 1 Level 2 symbol. Limit 10 packs |

## Market data lines

A market data line is one concurrent streamed instrument, counted across TWS and the API together. Every account starts with a minimum of 100 lines. After the first month of trading the allowance is the greatest of monthly USD commissions divided by 8, USD equity multiplied by 100 divided by 1,000,000, or 100. TWS shows current usage with Ctrl, Alt and = on Windows and Linux, or CMD, OPTION and + on macOS. [How market data is allocated](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated) · [market data lines introduction](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/introduction)

Market depth and tick-by-tick requests scale with the line count. At 100 lines the caps are 5 tick-by-tick subscriptions and 3 simultaneous Level 2 symbols. At 1100 or more lines they reach 60 and 60. [Specialized market data lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines)

More lines come from Quote Booster packs at USD 30.00 each. A pack adds 100 Level 1 quotes and 1 Level 2 symbol, works in the desktop systems and the API, and is capped at 10 packs per account. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

## Errors you will hit

| Code | Message | What to do |
| --- | --- | --- |
| 101 | Max number of tickers has been reached. | The line allowance is exceeded. Check active lines in TWS with Ctrl, Alt and =. |
| 10089 | Requested market data requires additional subscription for API. Delayed market data is available. | The subscription is missing or does not cover API use. Add the subscription, or switch to delayed data. |
| 10197 | No market data during competing session. | The paper account and the live account are both requesting live data. Preference goes to the live account. |

Source: [error codes](https://ibkrcampus.com/docs/tws-api/doc/error-handling/error-codes). The 10089 resolution is also on the [common error resolution page](https://ibkrcampus.com/docs/tws-api/doc/error-handling/common-error-resolution/requested-market-data-requires-additional-subscription-for-api-see-link-in-market-data-connections-dialog-for-more-details-delayed-market-data-is-available).

## Reference detail

### Subscriber status

IBKR classifies everyone as a professional market data user by default. An individual who believes they qualify as non-professional must change the status in Client Portal. Corporations, LLCs, partnerships, and any account using the data beyond personal investment are professional. A person is professional if they are registered with the SEC, the CFTC, a state securities agency, a securities exchange or association, or a commodities or futures market or association; if they act as an investment advisor under Section 201(11) of the Investment Advisor's Act of 1940; or if they work for a bank or another registration-exempt organization in a role that would otherwise require registration. [Professional vs non-professional](https://ibkrcampus.com/docs/general/market-data-subscriptions/professional-vs-non-professional) · [market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php) · [guidelines on subscriber classifications](https://ibkrguides.com/kb/guidelines-on-market-data-subscriber-classifications.htm)

The professional rate relates to exchange market data status, not to the IBKR Pro or IBKR Lite account tier. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

### Delayed data

Delayed data is a fallback when a real-time subscription is missing. `reqMarketDataType` type 3 tells TWS to fall back to delayed data, signalled by a `marketDataType` callback; the four types are 1 live, 2 frozen, 3 delayed and 4 delayed frozen. Delayed data is 15 to 20 minutes old and arrives as tick types 66 to 76. It works with `reqMktData` and `reqHistoricalData` only, not with tick-by-tick requests. Availability is per exchange, and IBKR no longer offers delayed US equity quotes to Interactive Brokers LLC clients, so a US equity strategy cannot lean on free delayed quotes. [Delayed market data introduction](https://ibkrcampus.com/docs/tws-api/doc/market-data-delayed/introduction) · [market data type behavior](https://ibkrcampus.com/docs/tws-api/doc/market-data-delayed/market-data-type-behavior) · [subscribing to data](https://www.interactivebrokers.com/campus/trading-lessons/subscribing-to-data/) · [market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

### Paper accounts

A paper account has its own login and USD 1,000,000 of simulated equity. Its trading permissions, market data and base currency mirror the live account, and it exists only as an attachment to an approved live account. An unfunded account can use the paper account for delayed level 1 and historical data only. Market data from the live account can be shared with one paper account, configured under Paper Trading Account settings, and the two logins cannot use the same subscription at the same time. That clash is error 10197. [Requesting a paper trading account](https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/) · [market data sharing](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing) · [paper trading API limitations](https://ibkrcampus.com/docs/tws-api/doc/notes-limitations/limitations/paper-trading) · [error codes](https://ibkrcampus.com/docs/tws-api/doc/error-handling/error-codes)

### Snapshots

Regulatory snapshots are a pay-per-request path. The fifth `reqMktData` argument requests a calculated US stock NBBO snapshot at USD 0.01 each, charged on live and paper accounts, capped at 150 per month for a non-professional and 4500 for a professional on NYSE, with AMEX and NASDAQ at 2300 professional. Two official pages disagree on coverage: the TWS API page says US stocks and options, the subscriptions page says common US stocks only and not ETFs, options or futures. [Regulatory snapshots](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/top-of-book-l-1/regulatory-snapshots) · [regulatory snapshots, subscription page](https://ibkrcampus.com/docs/general/market-data-subscriptions/regulatory-snapshots)

### Bundles and extras

The US Securities Snapshot and Futures Value Bundle includes snapshot data for Consolidated Tapes A, B and C, plus OPRA US options, OTC Markets, CBOE Market Data Express indices, US bond quotes and Dow Jones indices. NYSE Network A, Network B, NASDAQ Network C and OPRA are part of it, and the professional bundle leaves out Dow Jones. The Add-On Streaming Bundle is described as containing all three equity networks and OPRA and requires the snapshot bundle, and for options and futures the underlying index is not included. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php) · [popular market data subscriptions](https://ibkrcampus.com/docs/general/market-data-subscriptions/popular-market-data-subscriptions/introduction)

Research and news subscriptions sit in a separate catalogue on the [research and news page](https://www.interactivebrokers.com/en/pricing/research-news-services.php). The public page labels each provider Free or Paid and publishes no fixed monthly price for the paid ones.
