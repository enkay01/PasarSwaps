# The easiest paper trading and backtesting path

Status: research finding
Evidence checked: 2026-09-16

## Short answer

Yes, a path exists that needs neither a gateway process nor a funded brokerage account. An Alpaca Paper Only account needs an email address, and its paper endpoint is an HTTP API, so nothing runs locally except the script that calls it. Five steps take a beginner from a backtest to a live paper loop.

Webull gives a paper account inside its app, and its documentation does not mention a deposit. Tradier has a free sandbox with a USD 0 account minimum, but it asks for an approved Tradier Brokerage account first. TradeStation and Interactive Brokers tie simulated trading to a funded live account. tastytrade and Coinbase document no simulated account at all. Kraken has no spot paper mode; its futures demo environment was decommissioned on 14 July 2026.

## Paper trading accounts

All rows checked 2026-09-16. Funding means money in a live brokerage account.

| Broker | What the paper account needs | Funding | Paper asset classes | Source |
| --- | --- | --- | --- | --- |
| Alpaca | Sign up with an email address. A separate API key and the endpoint `https://paper-api.alpaca.markets` | None | US stocks, ETFs, options, crypto | [Paper trading](https://docs.alpaca.markets/docs/paper-trading) |
| Tradier | An approved Tradier Brokerage account, then a sandbox token and the endpoint `https://sandbox.tradier.com/v1` | None. Account minimum is USD 0. An account left unfunded for more than 60 days gets a limited online experience | US equities, ETFs, options | [Endpoints](https://docs.tradier.com/docs/endpoints) · [FAQ](https://docs.tradier.com/docs/faq) · [Pricing](https://tradier.com/individuals/pricing) |
| Webull | A Webull account, then paperTrade mode in the mobile app, desktop app, or web | None stated | US stocks, ETFs, options, crypto, futures, event contracts | [paperTrade](https://www.webull.com/paper-trading) · [Help FAQ](https://www.webull.com/help/faq/11069) |
| Charles Schwab | A Schwab client login on thinkorswim. Non-clients can get a free 30-day guest pass | None stated | Stocks, options, futures, forex | [paperMoney](https://www.schwab.com/trading/thinkorswim/paper-trading) |
| TradeStation | A funded TradeStation brokerage account | Required | Stocks, options, futures | [Simulated trading](https://www.tradestation.com/platforms-and-tools/simulated-trading/) |
| Interactive Brokers | An approved live account. The API also needs Trader Workstation or IB Gateway running | Required. An unfunded account can use the paper account for delayed level 1 and historical data only | Stocks, options, futures, forex, bonds | [Requesting a paper trading account](https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/) |
| tastytrade | None. No simulated environment exists | Not applicable | Not applicable | [Does tastytrade offer paper trading?](https://support.tastytrade.com/support/s/solutions/articles/43000498775) |
| Coinbase | None. No paper environment is documented for retail accounts | Not applicable | Not applicable | [Coinbase brokerage](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/coinbase) |
| Kraken | The Kraken CLI local paper engine. No account and no API keys. macOS and Linux only | None | Crypto spot and futures | [Kraken CLI](https://www.kraken.com/kraken-cli) |

Alpaca is the only one on the list that separates the paper account from a live account entirely. The documentation states that anyone globally can create a Paper Only account with an email address, that the paper account starts at USD 100,000, and that the same API key and endpoint change moves the same code to live later. The Paper Only account receives IEX market data only, not consolidated data. Options are enabled in paper by default, and a live options level needs a separate request. [Paper trading](https://docs.alpaca.markets/docs/paper-trading) · [Options](https://docs.alpaca.markets/docs/options-trading)

Tradier's sandbox is one signup away from live, but the signup is a brokerage application. The getting started page says to create an account and generate both a production token and a sandbox token, and the FAQ says every Tradier Brokerage account holder can create a paper account. The sandbox serves 15-minute delayed data and has no delayed streaming endpoint. The pricing page lists a USD 0 account minimum and warns that an account unfunded for more than 60 days gets a limited online experience. [Getting started](https://docs.tradier.com/docs/getting-started) · [FAQ](https://docs.tradier.com/docs/faq) · [Pricing](https://tradier.com/individuals/pricing)

Webull's paperTrade page describes unlimited virtual funds, a reset at any time, Level 2 data, and multi-leg options, and it lists the feature as free. Two steps are involved: sign up, then switch to paperTrade. The pages do not state a deposit requirement. [paperTrade](https://www.webull.com/paper-trading)

Schwab's paperMoney gives USD 100,000 of virtual buying power and runs inside thinkorswim, which is a desktop, web, and mobile platform. The Schwab pages say it is free and built in for Schwab clients, and they do not state that the brokerage account must be funded. A non-client can get a 30-day guest pass. No paper API is documented. [paperMoney](https://www.schwab.com/trading/thinkorswim/paper-trading)

TradeStation states the funding rule directly. The footnote on its simulator page says the simulator is only available to customers who have funded their TradeStation brokerage account, and the help pages say simulated trading works only on symbols covered by the account's real-time data entitlements. [Simulated trading](https://www.tradestation.com/platforms-and-tools/simulated-trading/) · [Simulated trading help](https://help.tradestation.com/10_00/eng/tradestationhelp/desktop/simulated_trading.htm)

Interactive Brokers behaves the same way. The earlier note in this repo found that a paper account exists only as an attachment to an approved live account, and that an unfunded account gets delayed level 1 and historical data only. The API needs Trader Workstation or IB Gateway, which is the gateway process this ticket is trying to avoid. [IBKR market data subscriptions](../ibkr/market-data-subscriptions.md)

tastytrade is a clear negative. Its support page says tastytrade does not provide a simulated or paper trading platform. [Does tastytrade offer paper trading?](https://support.tastytrade.com/support/s/solutions/articles/43000498775)

Coinbase is also a negative. QuantConnect's Coinbase brokerage page states that the Coinbase brokerage does not support paper trading, and Coinbase's own help center documents no simulator. The QuantConnect statement is the only source found, and it is a platform's documentation rather than Coinbase's. [Coinbase brokerage](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/coinbase)

Kraken's position changed this year. Its derivatives demo environment at `demo-futures.kraken.com` was scheduled for decommissioning at 13:00 UTC on Monday 14 July 2026, and that date has passed. Kraken Pro spot has no demo. The newer Kraken CLI ships a local paper engine for spot and futures that runs against live prices, needs no credentials, and states that no Kraken account is required. The install detects the operating system and supports macOS and Linux, and Kraken labels the tool experimental. [API testing environment](https://support.kraken.com/articles/360024809011-api-testing-environment-derivatives) · [Kraken CLI](https://www.kraken.com/kraken-cli)

## What a first backtest costs

All rows checked 2026-09-16. Steps count from a working Python install.

| Library | Install and data | Backtest to paper | Steps | Source |
| --- | --- | --- | --- | --- |
| backtesting.py | `pip install backtesting`. You supply OHLC data; a sample of Alphabet shares ships with the package | No paper or broker path | 3 | [Project page](https://kernc.github.io/backtesting.py/) |
| vectorbt | `pip install vectorbt`. Data can be pulled with `vbt.YFData.download` | Community edition documents no paper or live path | 3 | [Repository](https://github.com/polakowo/vectorbt) |
| Backtrader | `pip install backtrader`. Data from CSV, Yahoo, or a pandas frame | Live path supports Interactive Brokers, Visual Chart, and Oanda only. The IB route needs IbPy and TWS or IB Gateway | 4 | [Quickstart](https://www.backtrader.com/docu/quickstart/quickstart/) · [Live trading](https://www.backtrader.com/docu/live/live/) · [PyPI](https://pypi.org/project/backtrader/) |
| Zipline-reloaded | `pip install zipline-reloaded`, then a free NASDAQ Data Link API key and `zipline ingest -b quandl` | Backtest only. Quantopian's hosted live engine closed in 2020 | 5 | [Repository](https://github.com/stefan-jansen/zipline-reloaded) |
| NautilusTrader | `pip install nautilus_trader` on Python 3.12 to 3.14, then load data into a Parquet catalog | One strategy runs in `BacktestNode` and `TradingNode`. Adapters list Interactive Brokers for traditional markets and many crypto venues, and no Alpaca | 5 or more | [Documentation](https://nautilustrader.io/docs/latest/) · [Integrations](https://nautilustrader.io/docs/latest/integrations/) |
| QuantConnect LEAN | `pip install --upgrade lean`, plus Docker for local runs | One algorithm runs in backtest, paper, and live. The CLI documentation states a paid organization tier is required | 6 or more | [Installing LEAN CLI](https://www.quantconnect.com/docs/v2/lean-cli/installation/installing-lean-cli) |

The three steps for backtesting.py are install the package, write a `Strategy` class with `init` and `next`, then call `Backtest(...).run()` and `.plot()`. A dual moving average example runs about 25 lines, and the page prints the full output columns for each run. It reads any OHLC series, and it has no broker connection at all. [Project page](https://kernc.github.io/backtesting.py/)

vectorbt has the same shape. Install, download price data, then pass entry and exit signals to `vbt.Portfolio.from_signals`. Its examples use `vbt.YFData.download`, so the data step does not need a key. The community edition is the free one; a separate VectorBT PRO exists. [Repository](https://github.com/polakowo/vectorbt)

Backtrader adds a data feed and a Cerebro engine to set up before the strategy. Its live trading documentation lists Interactive Brokers, Visual Chart, and Oanda as the only live paths, and the IB route needs IbPy plus a running TWS or IB Gateway. The last PyPI release is 1.9.78.123, uploaded 19 April 2023. [Live trading](https://www.backtrader.com/docu/live/live/) · [PyPI](https://pypi.org/project/backtrader/)

Zipline-reloaded is a backtest engine now. Its README says Quantopian used it for live trading until the fund closed in late 2020, and the documented workflow is ingest a data bundle with a NASDAQ Data Link key and then run a script file with `zipline run`. [Repository](https://github.com/stefan-jansen/zipline-reloaded)

NautilusTrader is the one library here whose own documentation states that the same execution semantics and time model apply in backtests and live systems. The high-level API needs a Parquet data catalog before the first backtest, which is more preparation than the three-step libraries. The integration table lists Interactive Brokers for multi-venue brokerage and Databento for data, alongside crypto venues. An Interactive Brokers paper run reintroduces the funded-account and gateway requirements, so the library does not by itself solve this ticket's constraint. [Documentation](https://nautilustrader.io/docs/latest/) · [Integrations](https://nautilustrader.io/docs/latest/integrations/) · [Getting started](https://nautilustrader.io/docs/latest/getting_started/)

QuantConnect LEAN reproduces a QuantConnect algorithm locally, but the installation page states that users must be on a paid organization tier, and local runs download a Docker image of the engine. The same algorithm source runs in backtest, paper, and live. [Installing LEAN CLI](https://www.quantconnect.com/docs/v2/lean-cli/installation/installing-lean-cli)

## Platforms that run both modes from one codebase

All rows checked 2026-09-16.

| Platform | Asset classes | Paper mode | Setup | Source |
| --- | --- | --- | --- | --- |
| QuantConnect | US equities, options, futures, forex, crypto, CFD | Cloud paper brokerage with simulated fills, no brokerage account needed | Browser signup and backtest are free. Paper needs a live trading node, and the Free Plan lists zero | [Pricing](https://www.quantconnect.com/pricing) · [Paper brokerage](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading) |
| Freqtrade | Crypto spot and futures only | Dry-run mode on the same strategy file as the backtest | Docker, compose file, image pull, user directory, config, data download, backtest, then dry-run | [Home](https://www.freqtrade.io/en/stable/) · [Docker quickstart](https://www.freqtrade.io/en/stable/docker_quickstart/) |
| Hummingbot | Crypto only | Paper connectors for Binance, KuCoin, Kraken, and Gate.io. Exchange API keys are not needed for paper on the market-making strategies | Docker or source install, then pick a `_paper_trade` connector | [Paper trade](https://hummingbot.org/client/global-configs/paper-trade/) |
| OctoBot | Crypto only | Cloud paper runs on virtual funds with no exchange credentials | Create an account, pick strategies, start a paper bot | [Paper trading](https://www.octobot.cloud/en/blog/paper-trading-with-octobot) · [Simulator](https://www.octobot.cloud/en/guides/octobot-usage/simulator) |
| Blankly | Stocks, crypto, forex claimed | README claims one codebase for backtest, paper, sandbox, and live, with Alpaca paper listed as working | `pip install blankly`, then `blankly init`, then add exchange keys | [Repository](https://github.com/blankly-finance/blankly) |

QuantConnect is the only platform on this list that covers US equities and options with the same algorithm in backtest and paper. The paper brokerage page says the paper account needs no brokerage signup and supports US equities and futures among other classes, but the pricing comparison marks paper trading as unavailable on the Free Plan and lists the Free Plan's live trading node limit as zero. The paid tiers include it. [Paper brokerage](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading) · [Pricing](https://www.quantconnect.com/pricing)

Freqtrade, Hummingbot, and OctoBot are crypto only. Freqtrade's supported exchange list is Binance, BingX, Bitget, Bybit, Gate, HTX, Hyperliquid, Kraken, OKX, and community-tested Bitvavo and KuCoin. Hummingbot's paper connectors cover four crypto exchanges. OctoBot runs against Binance, Hyperliquid, and other crypto exchanges. None of the three documents a US equity or US option path. [Freqtrade exchanges](https://www.freqtrade.io/en/stable/) · [Hummingbot paper trade](https://hummingbot.org/client/global-configs/paper-trade/) · [OctoBot](https://github.com/drakkar-software/octobot)

Blankly claims the one-codebase pattern across backtest and paper, and its supported exchange table gives Alpaca paper trading a working mark. Treat the claim with care. The same README still lists FTX and Coinbase Pro as supported exchanges, and it says the package is tested on Python 3.7 to 3.10. Those are stale markers. [Repository](https://github.com/blankly-finance/blankly)

## Ranked by setup work

The fewest steps for a free paper account are Alpaca, at three: sign up with an email, open a paper account and generate its keys, then point `APCA_API_BASE_URL` at `https://paper-api.alpaca.markets`. No application, no deposit, no local process.

Webull is two steps but lives in an app, so it does not connect to a backtest. Tradier is three steps and adds an account application plus a 15-minute data delay. Schwab is two steps if a Schwab account already exists, and it has no paper API. TradeStation and Interactive Brokers sit at the bottom because both require funding, and the IBKR API adds Trader Workstation or IB Gateway.

Among backtesting libraries, backtesting.py and vectorbt are three steps each, and neither reaches a broker. Backtrader is four steps and reaches only IBKR, Visual Chart, and Oanda. Zipline-reloaded is five steps and backtests only. NautilusTrader and QuantConnect LEAN each need five or more steps and a data catalog or Docker before the first run.

Among whole-loop platforms, QuantConnect has the lowest step count for US equities and options if the subscription is acceptable, because the algorithm is written and backtested in the browser. Freqtrade has the lowest step count overall for a free one-codebase loop across backtest and dry-run, and it is crypto only.

## The easiest start-to-finish path

For US equities and options, take an Alpaca Paper Only account and write the backtest as a plain Python function over daily bars. The whole path is five steps. Sign up with an email address. Open a new paper account and copy its key and secret. `pip install alpaca-py` and pull daily bars through the free IEX feed. Write the signal rules once as a function that takes a price frame and returns entries and exits, and run it over history. Then loop the same rules over new bars and send orders through `alpaca-py` pointed at the paper endpoint. When the results hold up, the code moves to a live Alpaca account by changing the endpoint and keys.

This is the only path on the list that combines a free paper account, no funding, no gateway, one language, and options. It also covers what the earlier build survey found in Alpaca tutorials: a separate paper host, a separate key, and the same SDK calls in both environments. [Paper trading](https://docs.alpaca.markets/docs/paper-trading)

The catches are concrete. Paper fills are a simulation. Alpaca states that paper trading does not account for market impact, information leakage, slippage from latency, queue position on non-marketable limit orders, price improvement, regulatory fees, or dividends. Limit orders fill only when they become marketable, order size is not checked against NBBO size, and about 10 percent of eligible orders receive a random partial fill. [Paper trading](https://docs.alpaca.markets/docs/paper-trading)

A Paper Only account receives IEX data only, which is a slice of the consolidated tape, so a backtest on that feed sees one venue's quotes. The documentation lists this as an entitlement limit of the Paper Only account. [Paper trading](https://docs.alpaca.markets/docs/paper-trading)

Options work in paper by default, so the paper loop can trade them without an approval step. A live options level is a separate request with its own approval, and the live trading level controls which spreads the account may open. [Options](https://docs.alpaca.markets/docs/options-trading)

The backtest and the paper loop are two files. The signal function is shared, and the order calls are not, because a backtester has no broker. That gap is where a paper result can drift from the backtest even before the fill assumptions above are counted.

If the goal is crypto rather than US equities, Freqtrade removes even the two-file gap. One strategy file runs the backtest, then the dry-run, then live, with no account and no keys until the live step. The cost is that the whole path starts with Docker, and the strategy is limited to crypto pairs.
