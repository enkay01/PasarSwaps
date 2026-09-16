# IBKR market data subscriptions and permissions

Status: research finding
Evidence checked: 2026-09-16

## Scope

This note answers what a small research lab needs before it can pull Interactive Brokers market data through the API: which subscriptions exist, what they cost, how professional and non-professional status changes the bill, how market data lines work, what the API returns when something is missing, how delayed data behaves, and how a paper account relates to the live account. Every price and rule below comes from an Interactive Brokers page. Prices change, so the date checked is part of each number.

## Short answer

You need an approved and funded live account. Demo accounts cannot subscribe to data, the account must be the IBKR Pro type, and most individuals need USD 500 of equity beyond the cost of the subscriptions. The API also needs a signed Market Data API Acknowledgement, or requests come back saying the market data is not subscribed. [Market data requirements](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-requirements) · [Market Data API Acknowledgement](https://ibkrcampus.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement)

US equities have a free tier and a consolidated tier. The free real-time stream from Cboe One and IEX is non-consolidated, so it does not show the NBBO. Consolidated NBBO comes from the per-network subscriptions, NYSE Network A, Network B, and NASDAQ Network C, each USD 1.50 per month for a non-professional, or from the US Securities Snapshot and Futures Value Bundle at USD 10.00 plus USD 0.01 per snapshot. To stream those consolidated quotes through the API you add the US Equity and Options Add-On Streaming Bundle at USD 4.50 non-professional or USD 125.00 professional. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

Options need OPRA. The OPRA (US Option Exchanges) Level 1 subscription covers all US options in one product, USD 1.50 non-professional and USD 32.75 professional. An option chain does not need a subscription per underlying. The underlying price still comes from the equity subscription for that symbol, and IBKR states that Greeks need a subscription for both the underlying and the derivative. [Understanding market data subscriptions](https://ibkrcampus.com/docs/general/market-data-subscriptions/understanding-market-data-subscriptions)

Professional status can multiply the price. The Add-On Streaming Bundle is USD 4.50 non-professional against USD 125.00 professional, and OPRA is USD 1.50 against USD 32.75. IBKR classifies every user as professional by default until they change it in Client Portal. [Professional vs non-professional](https://ibkrcampus.com/docs/general/market-data-subscriptions/professional-vs-non-professional)

Market data lines cap how much can stream at once across TWS and the API. Every account starts with 100, and the allowance grows with commissions or equity. Buying more means Quote Booster packs at USD 30.00 each, up to 10 per account. Running out returns error 101, the max number of tickers error. [How market data is allocated](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated) · [Error codes](https://ibkrcampus.com/docs/tws-api/doc/error-handling/error-codes)

A paper account mirrors the live account's trading permissions and base currency, and its market data can be shared from the live account at no extra cost. The two cannot use the shared data at the same time, and that clash returns error 10197. [Requesting a paper trading account](https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/) · [Market data sharing](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing)

## Subscriptions and monthly prices

Prices checked 2026-09-16. All figures are USD per month unless noted. Source for every row in this table is the [market data pricing page](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php) unless the last column says otherwise.

| Subscription | Non-professional | Professional | Notes | Source |
| --- | --- | --- | --- | --- |
| US Real-Time Non-Consolidated Streaming Quotes | Free | Free | Cboe One and IEX, no NBBO | pricing page |
| Cboe One (L1) | 1.00 | 5.00 | Single venue, non-consolidated | pricing page |
| Cboe One Add-On Bundle (L1) | 1.00 | 5.00 | Requires the snapshot bundle | pricing page |
| US Securities Snapshot and Futures Value Bundle | 10.00 base, waived for activity, plus 0.01 per snapshot | not offered | Non-professional product. Waived at USD 30.00 monthly commissions | pricing page |
| Professional US Securities Snapshot Bundle | not offered | 10.00 base, waived for activity, plus 0.01 per snapshot | Professional counterpart. Waived at USD 30.00 monthly commissions | pricing page |
| US Futures Value Bundle PLUS | 5.00 | not offered | Requires the snapshot bundle | pricing page |
| US Equity and Options Add-On Streaming Bundle | 4.50 | 125.00 | Adds streaming. Waived above USD 5.00 non-professional and USD 15.00 professional commissions | pricing page |
| OPRA (US Option Exchanges) (L1) | 1.50 | 32.75 | All US options. Fee waived for all users when the account generates USD 20.00 monthly commissions | pricing page |
| NYSE (Network A/CTA) (L1) | 1.50 | 45.00 | NYSE listed | pricing page |
| NYSE American, BATS, ARCA, IEX and Regional Exchanges (Network B) (L1) | 1.50 | 25.00 | ARCA, AMEX, BATS, IEX and regionals | pricing page |
| NASDAQ (Network C/UTP) (L1) | 1.50 | 25.00 | NASDAQ listed | pricing page |
| ISE Options (L1, L2) | 11.50 | 60.00 | Single options exchange depth | pricing page |
| NASDAQ Options Market (L1, L2) | 11.50 | 62.50 | Single options exchange depth | pricing page |
| NYSE AMEX Options (L1, L2) | 11.50 | 62.50 | Single options exchange depth | pricing page |
| NYSE Arca Options (L1, L2) | 11.50 | 62.50 | Single options exchange depth | pricing page |
| Quote Booster pack | 30.00 per pack | 30.00 per pack | Adds 100 Level 1 quotes and 1 Level 2 symbol. Limit 10 packs | pricing page |
| Snapshot quotes | 0.01 US equities and ETFs, 0.03 other | same | Up to 100 free per month, USD 1.00 monthly waiver, auto-upgrade to streaming if snapshot spend reaches the streaming price | pricing page |

The bundle footnotes on the pricing page say the US Securities Snapshot and Futures Value Bundle includes snapshot data for Consolidated Tapes A, B, and C, and also includes OPRA US options, OTC Markets, CBOE Market Data Express indices, US bond quotes, and Dow Jones indices. The Professional bundle leaves out Dow Jones. Footnote 23 on the same page lists NYSE Network A, Network B, NASDAQ Network C, and OPRA as part of the bundle. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

The common subscription list describes the US Equity and Options Add-On Streaming Bundle as containing all three equity networks and OPRA, and says it requires the snapshot bundle. It also states that for options and futures the underlying index is not included. [Popular market data subscriptions](https://ibkrcampus.com/docs/general/market-data-subscriptions/popular-market-data-subscriptions/introduction)

Regulatory snapshots are a separate pay-per-request path. The fifth argument of `reqMktData` requests a calculated US stock NBBO snapshot for USD 0.01 per request, charged on live and paper accounts alike, capped at 150 per month for a non-professional and 4500 for a professional on NYSE, with AMEX and NASDAQ at 2300 professional. [Regulatory snapshots](https://ibkrcampus.com/docs/tws-api/doc/market-data-live/top-of-book-l-1/regulatory-snapshots) Two official pages then disagree on coverage. The TWS API page says the request covers US stocks and options. The market data subscriptions page says regulatory snapshots are not available for ETFs, options, futures, or anything other than common US stocks. [Regulatory snapshots, subscription page](https://ibkrcampus.com/docs/general/market-data-subscriptions/regulatory-snapshots)

Research and news subscriptions are a separate catalogue of vendor products on the [Research and News page](https://www.interactivebrokers.com/en/pricing/research-news-services.php). The public page labels each provider Free or Paid and does not publish a fixed monthly price for the paid ones, so none can be listed here as a number.

## Market data lines

A market data line is one concurrent streamed instrument, and it is counted across TWS and the API together. Every account starts with a minimum of 100 lines. After the first month of trading the allowance is the greatest of monthly USD commissions divided by 8, USD equity multiplied by 100 divided by 1,000,000, or 100. [How market data is allocated](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/how-market-data-is-allocated)

TWS shows current usage with Ctrl, Alt and = on Windows and Linux, or CMD, OPTION and + on macOS. The documented example is a user with 100 lines, 50 symbols in a watchlist, and one API connection holding 25 lines, which leaves 25 lines for a second API connection. [Market data lines introduction](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/introduction)

Market depth and tick-by-tick requests scale with the line count. At 100 lines the caps are 5 tick-by-tick subscriptions and 3 simultaneous Level 2 symbols. At 500 lines they are 25 and 4. The table reaches 60 tick-by-tick and 60 Level 2 symbols at 1100 or more lines. [Specialized market data lines](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-lines/specialized-market-data-lines)

To buy more lines you buy Quote Booster packs at USD 30.00 each. Each pack adds 100 Level 1 quotes and 1 Level 2 symbol, works in the desktop systems and the API, and is capped at 10 packs per account. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

The error when lines run out is code 101, message "Max number of tickers has been reached." The notes say the active subscription count across TWS and the API has been exceeded, that it is calculated from equity, commissions, and Quote Booster packs, and that active lines can be checked in TWS with Ctrl, Alt and =. [Error codes](https://ibkrcampus.com/docs/tws-api/doc/error-handling/error-codes)

## API errors

The error codes page is the source for every row unless the last column says otherwise.

| Code | Message | What it means |
| --- | --- | --- |
| 101 | Max number of tickers has been reached. | Market data line allowance exceeded. |
| 10089 | Requested market data requires additional subscription for API. Delayed market data is available. | The user lacks a valid subscription, or the subscription does not cover API use. Requests should add the subscription or switch to delayed data. Source also the [common error resolution page](https://ibkrcampus.com/docs/tws-api/doc/error-handling/common-error-resolution/requested-market-data-requires-additional-subscription-for-api-see-link-in-market-data-connections-dialog-for-more-details-delayed-market-data-is-available). |
| 10090 | Part of requested market data is not subscribed. | Part of the request, for example a leg or a tick type, is not covered. |
| 10091 | Part of requested market data requires additional subscription for API. | The data exists on the account but does not extend to API use. See [TWS data vs API data](https://ibkrcampus.com/docs/general/market-data-subscriptions/tws-data-vs-api-data). |
| 354 | Requested market data is not subscribed. | No live data for that instrument. Check the Market Data Subscription Manager or use delayed data. |
| 10186 | Requested market data is not subscribed. Delayed market data is not enabled. | Subscription is missing and the session has not switched to delayed data. |
| 10187 | Failed to request historical ticks: No market data permissions. | Historical tick requests need permissions the account does not hold. |
| 10189 | Failed to request tick-by-tick data. Invalid Real-time Query. | TWS is connected from a different IP address, or market data permissions are missing. |
| 10197 | No market data during competing session. | The user is logged into the paper account and the live account at the same time and both request live data. Preference goes to the live account. |
| 10277 | News feed permissions required. | The news provider is not subscribed. |

Error 10167 and error 10168 do not appear on the current error codes page, so this note cannot confirm them from IBKR's own documentation. Messages still surface in community reports. The same situations are documented today as 354, 10089, 10186, and 10197, but IBKR does not label those as replacements.

## Delayed data

Delayed data is a fallback when a real-time subscription is missing. The TWS API exposes four market data types through `reqMarketDataType`: 1 live, 2 frozen, 3 delayed, and 4 delayed frozen. Type 3 requests tell TWS to fall back to delayed data when the user lacks the real-time subscription, and the switch is signalled by a `marketDataType` callback on the ticker. Delayed data is 15 to 20 minutes old and comes back as delayed tick types 66 to 76. Delayed and frozen data only work with `reqMktData` and `reqHistoricalData`, not with tick-by-tick requests. [Delayed market data introduction](https://ibkrcampus.com/docs/tws-api/doc/market-data-delayed/introduction) · [Market data type behavior](https://ibkrcampus.com/docs/tws-api/doc/market-data-delayed/market-data-type-behavior)

Delayed availability is per exchange. The pricing page lists OPRA at a 15 minute delay and most futures and non-US exchanges at 10 to 20 minutes. The same page states that IBKR no longer offers delayed quotation information on US equities to Interactive Brokers LLC clients, so a US equity strategy cannot rely on free delayed quotes. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

Delayed data is for level 1 top of book and historical data. An IBKR support reply on the campus subscription lesson states that delayed data is not available for tick-by-tick requests or level 2 market depth. [Subscribing to data](https://www.interactivebrokers.com/campus/trading-lessons/subscribing-to-data/)

## Professional and non-professional

IBKR classifies everyone as a professional market data user by default. An individual who believes they qualify as non-professional must change the subscriber status in Client Portal. By default, corporations, LLCs, partnerships, and any account using the data for more than personal investment are professional. A private person is professional if they are registered as a securities or investment advisor or act in a similar capacity, and an employee of a financial services business may also be professional. [Professional vs non-professional](https://ibkrcampus.com/docs/general/market-data-subscriptions/professional-vs-non-professional)

The pricing page gives the same split. A non-professional subscriber is a natural person, and the definition excludes corporations, trusts, organizations, institutions, and partnership accounts. The page then lists three disqualifiers that make a person professional: registration or qualification with the SEC, the CFTC, a state securities agency, a securities exchange or association, or a commodities or futures market or association; acting as an investment advisor under Section 201(11) of the Investment Advisor's Act of 1940; or employment by a bank or another registration-exempt organization to perform functions that would otherwise require registration. Any person who meets those criteria is a professional. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

The pricing page links a longer official guide on subscriber classifications. [Guidelines on market data subscriber classifications](https://ibkrguides.com/kb/guidelines-on-market-data-subscriber-classifications.htm)

A footnote on the professional fees row states that the professional rate relates to the exchange market data status, not to the IBKR Pro or IBKR Lite account tier. [Market data pricing](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

## Paper accounts

A paper account has its own login credentials and gets USD 1,000,000 of simulated equity. Trading permissions, market data, and base currency mirror the live account. A paper account only exists as an attachment to an approved live account, and an unfunded account can use the paper account for delayed level 1 and historical data only. [Requesting a paper trading account](https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/) · [Paper Trading API limitations](https://ibkrcampus.com/docs/tws-api/doc/notes-limitations/limitations/paper-trading)

Market data from the live account can be shared with one paper account, with one paper account allowed per live account. Sharing is configured on the live account under Paper Trading Account settings, and it must be turned on and pointed at a live username. When data is shared, the same subscription cannot serve the live and paper logins at the same time. [Market data sharing](https://ibkrcampus.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing) · [Requesting a paper trading account](https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/)

That conflict is the documented cause of error 10197. The error codes page says the user is logged into the paper account and the live account at the same time, both requesting live data, and preference goes to the live account. [Error codes](https://ibkrcampus.com/docs/tws-api/doc/error-handling/error-codes)

## What still needs checking

- The exact price of the paid research and news vendor subscriptions. The public catalogue shows Free or Paid only, so a lab that wants a specific provider must get the price from the subscription page after login.
- Whether error 10167 and error 10168 are still emitted by current TWS or Gateway builds. Neither appears on the current official error codes list, so this note treats them as unconfirmed. A capture from a live session would settle it.
- The 10197 behaviour when a paper account requests delayed data instead of live, while the live account is logged in. The error note only describes the live data case.
- Whether the US Securities Snapshot bundle's inclusion of OPRA gives usable option quotes or only a snapshot entitlement. The pricing footnote lists OPRA inside the bundle, while the common subscription list routes option streaming through OPRA and the Add-On Streaming Bundle. A subscription and one API request on a paper account would resolve the difference.
- Whether regulatory snapshots cover options. Two official IBKR pages give opposite answers, and the TWS API page and the subscription page are the ones in conflict. One request against an option contract would settle it.
- Current minimum equity rules per country. This note records the USD 500 individual minimum from the US pages. IBKR lists lower minimums for some account types and regions.
- Whether IBKR still sells line increases by any route other than Quote Booster packs. The pricing page names only the booster packs.
