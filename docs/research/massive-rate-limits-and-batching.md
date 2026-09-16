# Massive rate limits and batching for market downloads

Status: research finding
Evidence checked: 2026-08-31

## The answer

Massive Basic permits five REST requests per minute, and the [REST rate-limit guidance](https://massive.com/knowledge-base/article/what-is-the-request-limit-for-massives-restful-apis) says paid plans have unlimited REST requests but recommends staying below 100 requests per second. Massive does not say whether the Basic minute is a fixed or rolling window, and the public docs do not document quota response headers, a reset header, or a guaranteed `Retry-After`, so a downloader cannot depend on any of that behavior.

For a downloader, the working policy is one shared gate over every Massive request: 12.25 seconds between request starts on Basic, which sends about 4.90 requests per minute and leaves a small margin below the published maximum, and a paid gate capped at 95 request starts per second with eight concurrent HTTP workers. Batching is uneven. Historical stock and option aggregates and historical option trades each put one ticker in the path, so each needs one request per security or contract, while the grouped daily stock endpoint and the snapshot endpoints accept many tickers. Flat files are the bulk path for broad history. Stocks and Options are separate subscriptions, so the application needs one plan profile per asset class.

## What can be batched

| Repository need | Massive endpoint or delivery | Multiple securities in one request or file | Limit and pagination | Decision |
| --- | --- | --- | --- | --- |
| Historical stock daily bars | [`GET /v2/aggs/ticker/{stocksTicker}/range/...`](https://massive.com/docs/rest/stocks/aggregates/custom-bars) | No. The path contains one stock ticker. | Default 5,000 and maximum 50,000 base aggregates per page, with `next_url`. | Keep for narrow Security Lists and follow every page. |
| Historical stock daily bars | [`GET /v2/aggs/grouped/locale/us/market/stocks/{date}`](https://massive.com/docs/rest/stocks/aggregates/daily-market-summary) | Yes. It returns all US stocks for one trading date. | One date per request. No ticker-list parameter. | Use only when requests per date are fewer than requests per selected ticker. Filter the response locally. |
| Historical stock minute bars | [`GET /v2/aggs/ticker/{stocksTicker}/range/...`](https://massive.com/docs/rest/stocks/aggregates/custom-bars) | No. | Maximum 50,000 base aggregates. | There is no historical multi-stock minute REST request in the reviewed docs. |
| Current stock or option state | [`GET /v3/snapshot`](https://massive.com/docs/rest/stocks/snapshots/unified-snapshot) | Yes. The official Python example passes `ticker_any_of` with stock and option tickers. | Maximum 250 results per page and `next_url` pagination. | Useful for current snapshots only. It cannot replace historical bars. |
| Current full stock market state | [`GET /v2/snapshot/locale/us/markets/stocks/tickers`](https://massive.com/docs/rest/stocks/snapshots/full-market-snapshot) | Yes. `tickers` accepts a comma-separated list. An empty value returns more than 10,000 active tickers. | No ticker-count maximum or pagination is documented. | Good current-state batching, but not historical data. |
| Stock reference records | [`GET /v3/reference/tickers`](https://massive.com/docs/rest/stocks/tickers/all-tickers) | It can list all matching records, but the docs show one exact ticker or range filters rather than a comma-separated exact list. | Default 100, maximum 1,000, with `next_url`. | Use for reference discovery, not historical prices. |
| Option contract reference | [`GET /v3/reference/options/contracts`](https://massive.com/docs/rest/options/contracts/all-contracts) | The endpoint can list many contracts, but the documented `underlying_ticker` filter takes one underlying. There is no documented exact-list filter for several underlyings. | Default 10, maximum 1,000, with `next_url`. | Fetch each selected underlying and follow every page. An unfiltered full contract scan is not a practical substitute for an exact batch. |
| Historical option aggregates | [`GET /v2/aggs/ticker/{optionsTicker}/range/...`](https://massive.com/docs/rest/options/aggregates/custom-bars) | No. The path contains one option contract. | Maximum 50,000 base aggregates. | One REST request per contract and date slice. |
| Historical option trades | [`GET /v3/trades/{optionsTicker}`](https://massive.com/docs/rest/options/trades-quotes/trades) | No. The path contains one option contract. | Default 1,000, maximum 50,000, with `next_url`. | One paginated stream per contract. |
| Current option chain | [`GET /v3/snapshot/options/{underlyingAsset}`](https://massive.com/docs/rest/options/snapshots/option-chain-snapshot) | It returns the current chain for one underlying. | Default 10, maximum 250, with `next_url`. | It does not provide historical chain bars or trades. |

The endpoint name is not enough to prove batching. The historical stock and option aggregate paths each require one ticker, and a comma-separated list is not documented for either endpoint.

## Reference detail

### Request policy

The gate must wrap every Massive REST call, including custom date slices, option-contract pages, option aggregate calls, option-trade pages, retries, and pagination, because every pagination request counts as a request. A provider-level sleep between Securities is not sufficient, and a sleep outside `download_massive` is wrong because option work can make many requests inside one call. On HTTP 429, pause all Massive work, use `Retry-After` when the response carries a valid value, and otherwise wait 60 seconds before the first retry and then use capped exponential backoff with jitter. The HTTP seam has to expose the response status and headers to the request controller, since a JSON-only result cannot coordinate a global pause or read `Retry-After`.

Stocks and Options pricing is separate, so one `request_interval_seconds` value cannot represent a paid Stocks plan and a Basic Options plan at the same time; store a plan profile per asset class. The [Stocks pricing](https://massive.com/pricing?product=stocks) and [Options pricing](https://massive.com/pricing?product=options) pages confirm five requests per minute for each Basic plan and unlimited calls for each paid plan.

### Choosing per-ticker or grouped daily

Let `S` be the selected Security count and `D` the number of requested trading dates. Per-ticker custom bars need about `S` requests when each ticker fits below the 50,000-base limit, and grouped daily bars need `D` requests and return every US stock on each date. Choose grouped daily only when `D` is meaningfully lower than `S`. A broad 500-stock list over one year needs about 500 per-ticker requests or about 252 grouped-date requests, while a 30-stock list over two years needs about 30 per-ticker requests or about 504 grouped-date requests, which would be slower and download far more unused data. This choice applies only to daily bars, since Massive does not document a grouped historical minute endpoint.

### Bulk flat files

Massive states in its [Flat Files quickstart](https://massive.com/docs/flat-files/quickstart) that flat files are the bulk path for large historical jobs and REST is for smaller on-demand queries. Each compressed CSV covers one trading date and all securities in that asset class, and the importer can stream it and keep only the requested Security List.

- [Stock day aggregate files](https://massive.com/docs/flat-files/stocks/day-aggregates) and [stock minute aggregate files](https://massive.com/docs/flat-files/stocks/minute-aggregates) contain all US equities for one date at the given cadence. Stocks Starter, Developer, and Advanced include them, and Basic does not.
- Stock flat files hold unadjusted data, so the importer must apply CorporateActions locally if it needs the adjusted values that `adjusted=true` REST requests produce ([Stocks Flat Files overview](https://massive.com/docs/flat-files/stocks/overview)).
- [Option day aggregate files](https://massive.com/docs/flat-files/options/day-aggregates) and [option minute aggregate files](https://massive.com/docs/flat-files/options/minute-aggregates) contain all US option contracts for one date. Options Starter, Developer, and Advanced include them, and Basic does not.
- [Option trade files](https://massive.com/docs/flat-files/options/trades) contain all OPRA trades for one date. Options Developer and Advanced include them, and Basic and Starter do not.
- Flat files still need point-in-time contract reference data, including contract identity, expiration, strike, right, exercise style, multiplier, and adjusted deliverables for the contracts that survive local filtering.

### For the downloader

The current stock flow makes one custom-bars request per Security, which is the right REST shape for historical minute bars and narrow daily downloads. The current option flow lists contracts for one underlying and then requests minute aggregates for every returned contract, so on Basic one underlying can consume far more than five requests, and more threads would only produce HTTP 429 responses. The UI should estimate the contract and page count before work starts and warn when a Basic request is impractical. The transport should be chosen before requests are scheduled: per-ticker REST aggregates for narrow daily or minute stock work, grouped daily REST aggregates when `D` is meaningfully lower than `S`, stock flat files for broad paid stock history, per-contract REST or flat files for options depending on plan breadth, and serial REST at 12.25-second spacing for Basic option history with the lower-bound duration shown before start.
