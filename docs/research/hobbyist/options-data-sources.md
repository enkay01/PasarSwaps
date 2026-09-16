# Where a hobbyist gets options data

Status: research finding
Evidence checked: 2026-09-16

## Scope

This note is for one person with a laptop who wants to backtest a US options strategy this month and does not have an enterprise contract. It covers free sources and sources that cost under about USD 100 a month. The companion note [historical-options-and-event-data.md](../credit-spreads/historical-options-and-event-data.md) covers the institutional vendors and the import contract the lab needs. That note asks those vendors for quotes. This one records published prices where they exist and says so when the public pages do not. Every link below was fetched on 2026-09-16.

Two costs matter more than the headline price. A source that only returns chains for contracts that are still listed cannot be used for a strategy that held a position to expiry, because the contract disappears from the feed. A source whose historical rows carry no Greeks or implied volatility leaves that calculation to the reader. Both limits appear in the summary table and in the entries below.

## Summary

`No public statement` means the pages I checked do not say.

| Source | Cheapest useful tier | Cadence and history | Greeks and IV | Expired contracts | Signup and access |
| --- | --- | --- | --- | --- | --- |
| Yahoo Finance via yfinance | $0 | Current listed chains only | Not in the chain response | No public statement | None, `pip install yfinance` |
| Tradier | $0 with a brokerage account | Daily option candles for live contracts; intraday time and sales for 5 to 40 days | Greeks hourly, supplied by ORATS | No, the docs say expired options are not available | Funded-account application |
| Interactive Brokers | OPRA L1 at USD 1.50/month non-professional, waived at USD 20 commissions | Intraday bars while a contract is listed; no end-of-day option bars | Live only, no history | No, the docs list expired options as unavailable | IBKR account and USD 500 minimum equity |
| Cboe DataShop | Configurator, no public price | EOD and 15:45 snapshots, one-minute quotes, trades; from January 2010 per the FAQ | Optional paid add-on | Preserved for the dates purchased | Free account, then SFTP |
| Nasdaq Data Link (ORATS OSMV) | Price after login | Daily from 2013 | Included | No public statement | Nasdaq Data Link account |
| Massive | $29/month Starter, $199/month Advanced for quotes | Aggregates from 2014-06-02, quotes from 2022-03-07 | Current snapshots only | Reference data lists expired contracts | Account and API key |
| ThetaData | $0 free tier, $40/month for minute data | Free EOD from 2023-06-01, minute from 2020-01-01, tick from 2012-06-01 | Standard tier and up | No public statement | Account, no card for the free tier |
| ORATS | $99/month recurring near-EOD, or USD 599 one-time archive | Near-EOD from 2007, one-minute from August 2020 | Included | No public statement | Account |
| Databento | Pay as you go with USD 125 credit, USD 199/month Standard for live | Schema-dependent OPRA history from 2013 | Calculated locally | Timestamped definitions, survivorship is the lab's job | Account, onboarding in minutes |
| EODHD | USD 29.99/month early-adopter rate on the options add-on | 2.5+ years, since Q4 2023 | All five Greeks and IV | No public statement | Account, demo token without one |
| MarketData.app | $0 free tier, $30/month Trader billed monthly | Free 1 year, Starter 5 years, Trader unlimited | Current chains only, historical chains return null | No public statement | Account, 30-day trial without a card |
| Alpaca | $0 Basic, $99/month Algo Trader Plus | Historical options since February 2024 | No public statement | No public statement | Alpaca account |
| Alpha Vantage | USD 49.99/month for the historical options endpoint | Any date since 2008-01-01 | IV and delta, gamma, theta, vega, rho | No public statement | Account and premium key |

## Yahoo Finance and yfinance

Yahoo Finance is the zero-setup option. There is no signup and no key. The Python library `yfinance` wraps Yahoo's public endpoints, and the documentation shows a chain in one line: `yf.Ticker("MSFT").option_chain(dat.options[0]).calls` ([yfinance documentation](https://ranaroussi.github.io/yfinance/), [Ticker reference](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.html)). The `Ticker.options` attribute is the list of expirations that are currently listed.

Yahoo gets US options from OPRA through ICE Data Services, with a 15-minute delay, and its help page says the data must not be redistributed ([Exchanges and data providers](https://help.yahoo.com/kb/finance-for-web/exchanges-data-providers-yahoo-finance-sln2310.html)). The yfinance documentation repeats Yahoo's own warning that the finance API is intended for personal use only, and that yfinance is not affiliated with Yahoo ([yfinance documentation](https://ranaroussi.github.io/yfinance/), [Yahoo API terms](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm)).

The practical limit is history. The chain endpoint returns the expirations and strikes that exist now, so any contract that expired before today is outside the request. For a credit-spread backtest that needs the option that was short two months ago, this is the wrong source. It is a good way to spend five minutes learning the shape of a chain.

## Tradier

Tradier gives API access to any Tradier Brokerage account holder at no extra charge, and the broker's own plans start at $0 a month with a $0 account minimum ([Tradier FAQ](https://docs.tradier.com/docs/faq), [Tradier pricing](https://tradier.com/individuals/pricing)). The market data page says real-time data is available to all brokerage account holders and is not offered to anyone else, so the signup cost is the brokerage application rather than a subscription ([Market Data](https://docs.tradier.com/docs/market-data)).

Real-time equities and options, delayed data in the sandbox, and hourly Greeks supplied by ORATS are the documented fields. Historical option quotes are daily candles requested by OCC symbol, and the same page states that historical options data is not available for expired options ([Historical Data](https://docs.tradier.com/docs/historical-data)). Intraday time and sales run from 5 days at tick granularity to 40 days at 5 and 15 minutes. Level 2 is not offered ([Tradier FAQ](https://docs.tradier.com/docs/faq)).

Tradier is a reasonable choice for live paper trading or for pulling a chain for contracts that are still listed. It does not solve the expired-contract problem.

## Interactive Brokers

IBKR is cheaper than most people expect for the data, and worse than most people expect for the history. The non-professional OPRA top-of-book subscription is USD 1.50 a month, and it is waived once USD 20 of commissions are generated ([Market Data Pricing](https://www.interactivebrokers.com/en/pricing/research-news-marketdata.php)). A US Equity and Options Add-On Streaming Bundle is USD 4.50 for non-professionals, and the account needs USD 500 of equity to hold a market-data subscription. Delayed OPRA data is free, and the account gets 100 free snapshot quotes a month.

The history is the problem. IBKR lists expired options, end-of-day data for options, and time-and-sales beyond three years as unavailable historical data, so a contract has to be captured while it trades and stored locally ([IBKR options data for backtesting](../ibkr/options-data.md), [Unavailable Historical Data](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)). Live quotes arrive with implied volatility and all the Greeks, and there is no historical Greeks endpoint. The TWS API and the Web API can both discover chains. Nothing in the public docs describes a bulk historical option download.

For this repo the IBKR route is a capture pipeline, not a dataset purchase. If the strategy must be backtested over past expiries, IBKR alone cannot supply the data.

## Cboe DataShop

Cboe sells its own OPRA-derived files through a self-serve cart. The [Option EOD Summary](https://datashop.cboe.com/option-eod-summary) has a 15:45 ET snapshot and an end-of-day snapshot with NBBO bid and ask sizes, underlying bid and ask for stocks and ETFs, OHLC, volume, VWAP, and open interest. Implied volatility and Greeks are a paid calculation add-on. The product page says history from January 2012, while the [DataShop FAQ](https://datashop.cboe.com/faqs) coverage table gives January 2010 for Option EOD Summary, Option Quotes, and Option Trades. A buyer should treat the January 2010 figure from the FAQ table as the wider claim and confirm at purchase. Files arrive as CSV over SFTP, and the FAQ says files are removed 30 days after the order completes, so the buyer must archive them.

The price is computed by the purchase form from symbols, dates, cadence, calculation add-ons, and customer type. No public list price exists. That is a configurator, not a sales call, so a hobbyist can price a small symbol-and-date order without talking to anyone. A qualifying academic institution can ask about the academic discount ([DataShop FAQ](https://datashop.cboe.com/faqs)).

## Nasdaq Data Link

Nasdaq Data Link lists the ORATS Smoothed Options Market Quotes database, described as bid and ask prices, implied volatilities, volumes, open interest, and option Greeks for each trading day from 2013, and the ORATS Option Volatility Surfaces database ([OSMV](https://data.nasdaq.com/databases/OSMV), [OPT](https://data.nasdaq.com/databases/OPT)). The database pages do not show a price to a visitor. Nasdaq Data Link asks the visitor to log in to view publisher data sets and pricing, and the price is not published outside the account. I could not find a public figure for either database. For a hobbyist, the same underlying ORATS data is available directly at the prices below, so Nasdaq Data Link is a reseller path rather than a cheaper one.

## Massive

Massive, the platform formerly called Polygon.io, sells individual options plans at $0, $29, $79, and $199 a month ([Massive options pricing](https://massive.com/pricing?product=options), [Massive options](https://massive.com/options)). The free Basic plan returns end-of-day aggregates with two years of history. Starter at $29 adds 15-minute delayed data with two years. Developer at $79 extends aggregates to four years. Advanced at $199 is the tier that includes historical quotes, with full history ([Custom bars](https://massive.com/docs/rest/options/aggregates/custom-bars), [Quotes](https://massive.com/docs/rest/options/trades-quotes/quotes)).

The option quote history starts on 2022-03-07, and only the Advanced plan returns it. Aggregates go back to 2014-06-02, but aggregates are trade-derived OHLCV bars, not quotes, and the docs say a window with no qualifying trade produces no bar. The option-chain snapshot endpoint returns Greeks, implied volatility, and open interest, but the snapshot is a current reading delivered on a 15-minute delay at Starter and Developer and in real time at Advanced ([Option chain snapshot](https://massive.com/docs/rest/options/snapshots/option-chain-snapshot)). Historical Greeks and historical open interest are not part of the flat files, which matches the finding in the companion note.

For a hobbyist who needs cheap trade aggregates and a contract reference that includes expired contracts, the $29 and $79 tiers are useful. For a spread backtest that needs historical bid and ask, the entry point is $199.

## ThetaData

ThetaData runs a local terminal that serves its API, and it publishes a free tier. The free tier returns one year of end-of-day data for US stocks and options, from 2023-06-01, at a rate the same page gives as 20 requests a minute in the prose and 30 requests a minute in the table ([Subscriptions](https://docs.thetadata.us/Articles/Getting-Started/Subscriptions.html), [ThetaData](https://www.thetadata.net)). Signup does not require a credit card.

The paid individual plans are $40, $80, and $160 a month ([ThetaData pricing](https://www.thetadata.net/pricing)). Options history is 2020-01-01 at $40 for one-minute data, 2016-01-01 at $80 for tick data, and 2012-06-01 at $160. The endpoint table puts historical quote, open interest, and OHLC at the $40 tier, and implied volatility plus first-order Greeks at the $80 tier. The $160 tier adds second- and third-order Greeks and trade Greeks. Delivery is through the terminal with REST, a Python library, or flat files.

The free tier is the cheapest documented way to get a year of end-of-day option history without a card, and $40 buys six more years at one-minute granularity. The reviewed pages identify a contract by underlying, expiration, strike, and right, and do not describe a permanent contract identifier or delisted-underlying handling, so the lab still has to manage that itself.

## ORATS

ORATS sells the same research data it feeds its platform, and it publishes separate prices for the archive and the API. The near end-of-day set is a full chain 14 minutes before the close for more than 5,000 symbols from 2007. Recurring delivery is USD 99 a month, and the entire history from 2007 is USD 599 as a one-time purchase with access to the AWS S3 archive for 14 days ([Near End-of-day](https://orats.com/near-eod-data)). The one-minute intraday set starts in August 2020, costs USD 199 a month recurring, and the full historical archive is USD 1,500 one-time, with the page warning that S3 storage and transfer add USD 1,000 to USD 2,000 ([1 Minute Intraday](https://orats.com/one-minute-data)).

The API is a different product line with higher prices. The delayed data API is USD 199 a month with 20,000 requests, the live API is USD 299, and the live intraday API is USD 599 ([Options Data API](https://orats.com/data-api)). These are above the near-EOD archive price, so a backtester who only needs daily chains should look at the $99 recurring feed or the $599 one-time archive rather than the API.

The near-EOD fields include call and put bid and ask, open interest, a smoothed implied volatility, and delta, gamma, theta, vega, rho, and phi. ORATS documents a smoothed market values system in place of raw quotes and publishes errata for its bulk data, which the companion note covers. The pages reviewed here do not state whether expired contracts remain addressable in the archive.

## Databento

Databento sells OPRA history by usage, with a USD 125 signup credit that expires six months after signup ([Databento pricing](https://databento.com/pricing), [Usage-based pricing and credits](https://databento.com/docs/faqs/usage-pricing-and-data-credits)). Historical data is pay as you go and is charged by bytes delivered, so a small symbol universe and a short date range can cost a few dollars. Live access moved to subscriptions in June 2025, with a USD 199 a month Standard plan, and usage-based live access was discontinued for new users ([OPRA pricing plans](https://databento.com/blog/introducing-new-opra-pricing-plans)).

The schemas are raw market records rather than prepared chains. Databento does not publish option implied volatility or Greeks, so the lab calculates them. Definitions are timestamped, which is what makes point-in-time chain reconstruction possible, but instrument IDs are only unique within a day. The credit is enough to test a symbol or two and confirm the format before spending. For a hobbyist with a defined question and a small universe, Databento is the cheapest way to touch real OPRA ticks. For a broad historical chain study, the byte meter works against a small budget.

## EODHD

EODHD sells a US stock options add-on through its marketplace. The product page advertises 6,600+ US tickers, 42+ fields per contract, EOD OHLC, bid and ask with sizes, volume and open interest with day-over-day changes, all five Greeks, implied volatility, moneyness, and days to expiration ([US Stock Options Data API](https://eodhd.com/lp/us-stock-options-api)). The listing price is USD 29.99 a month against a USD 39.99 rate, described as an early-adopter discount while the product is in beta ([EODHD marketplace](https://eodhd.com/marketplace/unicornbay/options)).

Coverage is shorter than the other paid sources. The product page says 2.5+ years, since Q4 2023, and the marketplace page says two years, so a buyer should expect roughly late 2023 as the start. The API is JSON with a Python and Node SDK and an MCP server, and EODHD provides a demo token that returns AAPL contracts without signup, which is the quickest documented first chain of any paid source. Payment is card or PayPal, and a student can ask for 50 percent off ([EODHD pricing](https://eodhd.com/pricing)).

## MarketData.app

MarketData.app publishes a free tier with 100 API credits a day, one year of historical options data, and 24-hour delayed option chains, and it does not require a credit card for the 30-day trial ([Pricing](https://www.marketdata.app/pricing/)). The paid tiers are Starter at USD 12 a month on annual billing (USD 30 month to month) with 10,000 credits a day, five years of history, and 15-minute delayed options, and Trader at USD 30 a month on annual billing (USD 75 month to month) with 100,000 credits a day, unlimited history, and real-time options for non-professionals. Real-time access requires signing the OPRA agreement.

The chain endpoint takes a date parameter for historical end-of-day chains and returns OCC symbols, bid and ask with sizes, midpoint, last, volume, open interest, underlying price, and intrinsic and extrinsic value, with filters for expiration, strike, side, DTE, open interest, and volume ([Option Chain](https://www.marketdata.app/docs/api/options/chain/)). The docs state that Greeks and implied volatility are not stored historically, and that `iv`, `delta`, `gamma`, `theta`, and `vega` come back null on every historical request on every plan. The same page documents that historical open interest is the prior session's settled figure, published before the requested day opened, and that historical volume is the full-session total rather than a figure as of an intraday moment. That is a clearer statement of point-in-time semantics than most of the sources here publish.

The credit accounting is per option symbol for current data and one credit per 1,000 symbols for historical rows, so a one-year daily chain study across a few symbols fits inside the free tier. This is the cheapest documented route to historical chains with open interest, with the caveat that the reader supplies the Greeks.

## Alpaca

Alpaca's Basic market data plan is free with an Alpaca account, and Algo Trader Plus is USD 99 a month ([Alpaca market data](https://alpaca.markets/data), [About Market Data API](https://docs.alpaca.markets/docs/about-market-data-api)). Basic options coverage is the indicative pricing feed, described as a derivative of OPRA rather than actual quotes, with trades delayed 15 minutes and a websocket limit of 200 quotes. Algo Trader Plus switches options to the OPRA feed and raises the websocket limit to 1,000 quotes. Both plans allow 200 requests a minute on Basic and 10,000 on Algo Trader Plus.

The historical window is the constraint. The historical option data page says Alpaca has option history only since February 2024 ([Historical Option Data](https://docs.alpaca.markets/docs/historical-option-data)). For a strategy that needs older expiries, that is a short window, and the free indicative feed does not carry real quotes.

## Alpha Vantage

Alpha Vantage has a historical options endpoint that returns the full chain for one symbol and one date, with implied volatility and delta, gamma, theta, vega, and rho. It accepts any date since 2008-01-01, and output is JSON or CSV ([Alpha Vantage documentation](https://www.alphavantage.co/documentation/), Options Data APIs section). The endpoint is a premium function, so the free key's 25 requests a day do not reach it. The cheapest premium plan is USD 49.99 a month for 75 requests a minute ([Alpha Vantage premium](https://www.alphavantage.co/premium/)).

On the published description this is the longest cheap history of any source here, going back to 2008 at a plan under USD 100. The documentation does not state whether the response includes open interest, bid and ask sizes, or contracts that have since expired, and it does not publish a coverage count. A hobbyist should pull one dated chain and inspect the fields before relying on it.

## Where to start

Start with the two free tiers that return historical chains without a card or a brokerage account: [ThetaData](https://docs.thetadata.us/Articles/Getting-Started/Subscriptions.html) for a year of end-of-day option data and [MarketData.app](https://www.marketdata.app/docs/api/options/chain/) for a year of dated chains with open interest and documented point-in-time semantics. Both cost nothing to test, both return a first chain the same day, and the first paid step is USD 40 and USD 30 a month respectively if one year turns out to be too short. Yahoo Finance through `yfinance` is worth five minutes only to see the shape of a chain before signing up for anything.
