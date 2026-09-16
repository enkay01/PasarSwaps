# PasarSwaps

A research notebook for a one-person algorithmic trading project. The vocabulary is in `CONTEXT.md`, and it overrides synonyms. Research notes live in `docs/research/`, and decisions are recorded in `docs/adr/`.

## The first feature

Two commands put ten years of daily Bars for the S&P 500 on disk, then print the symbols whose MACD crossed on the latest Bar.

`python download.py` fetches the daily Bars from Alpaca and writes one Parquet file. It prints how many symbols it wrote and the date range.

`python screen.py` reads that file and prints the symbols with a fresh bullish MACD cross on the latest Bar, each with the date and the close, then prints the symbol count it read. The screen never touches the network.

## Setup

Python 3.11 or newer.

```
pip install -r requirements.txt
```

Copy `.env.example` to `.env.local` and fill in the two values the Alpaca dashboard shows.

```
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
```

Alpaca returns raw Bars by default and adjusts only when asked. The download names the adjustment instead of taking the default.

## Running

From the repository root:

```
python download.py
python screen.py
```

## The Dataset

`data/sp500_daily_bars.parquet` holds one row per symbol per date, with the columns symbol, date, open, high, low, close, volume and adjusted_close. The download makes one raw pass and one fully adjusted pass over each batch of symbols and stores the raw close beside the adjusted close, so the choice is visible in the file. The screen computes MACD on adjusted_close, because a split inside the window invents a cross that never happened.

`data/sp500_constituents.csv` is the Universe. It comes from the `datasets/s-and-p-500-companies` CSV, downloaded on 2026-09-16.

## Tests

```
pip install -r requirements-dev.txt
python -m pytest
```

## Limits

The download uses Alpaca's IEX feed, which carries about 2.5% of US market volume and withholds the last 15 minutes. It stops at the last completed calendar day, so a partial Bar for today never enters the Dataset.

The S&P 500 list holds today's members rather than the members on each past date, so a screen over history carries survivorship bias.

Commission and Slippage are zero, so no result accounts for the cost of trading.
