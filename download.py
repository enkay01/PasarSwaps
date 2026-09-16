"""Download ten years of daily Bars for the S&P 500 into one Parquet file.

    python download.py

Writes data/sp500_daily_bars.parquet and prints the symbol count and the date range.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
import os
from pathlib import Path
import sys

import pandas as pd
from dotenv import load_dotenv

from alpaca import DEFAULT_SETTINGS, AlpacaBarSource, AlpacaCredentials, RequestsTransport
from bars import BarSource, bars_to_frame
from paths import BARS_PARQUET, ENV_FILE, UNIVERSE_CSV
from store import DatasetSpan, dataset_span, write_bars
from universe import read_universe

API_KEY_VARIABLE = "ALPACA_API_KEY"
API_SECRET_VARIABLE = "ALPACA_API_SECRET"
TEN_YEARS = 10
SYMBOLS_IN_MESSAGE = 10


class IncompleteDownload(RuntimeError):
    """The Source returned no Bars for a symbol in the Universe."""


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    """The Universe to read and the file and window to write."""

    universe_path: Path
    bars_path: Path
    start: date
    end: date


def download_bars(source: BarSource, request: DownloadRequest) -> DatasetSpan:
    """Fetch the Universe and write one Parquet file, then report what landed."""
    symbols = read_universe(request.universe_path)
    bars = source.fetch_daily_bars(symbols, request.start, request.end)
    frame = bars_to_frame(bars)
    require_every_symbol(symbols, frame)
    write_bars(request.bars_path, frame)
    return dataset_span(frame)


def require_every_symbol(symbols: Sequence[str], frame: pd.DataFrame) -> None:
    """Refuse to store a Dataset that dropped a symbol the Universe asked for."""
    written = set(frame["symbol"].astype(str))
    missing = [symbol for symbol in symbols if symbol not in written]
    if missing:
        raise IncompleteDownload(
            f"the Source returned no Bars for {len(missing)} of {len(symbols)} symbols: "
            f"{', '.join(missing[:SYMBOLS_IN_MESSAGE])}"
        )


def ten_years_before(day: date) -> date:
    """The same day ten years earlier, moved to 28 February on a leap day."""
    try:
        return day.replace(year=day.year - TEN_YEARS)
    except ValueError:
        return day.replace(year=day.year - TEN_YEARS, day=28)


def read_credentials(environ: Mapping[str, str]) -> AlpacaCredentials:
    """Read the two Alpaca values, or say which one is missing."""
    api_key = environ.get(API_KEY_VARIABLE, "").strip()
    api_secret = environ.get(API_SECRET_VARIABLE, "").strip()
    if not api_key or not api_secret:
        raise RuntimeError(f"set {API_KEY_VARIABLE} and {API_SECRET_VARIABLE} in .env.local, then run again")
    return AlpacaCredentials(api_key=api_key, api_secret=api_secret)


def render(summary: DatasetSpan) -> str:
    """The one line the run prints when it finishes."""
    return f"wrote {summary.symbols} symbols, {summary.first_date} to {summary.last_date}"


def main() -> int:
    """Fetch the S&P 500 and write the Dataset."""
    load_dotenv(ENV_FILE)
    today = date.today()
    source = AlpacaBarSource(
        RequestsTransport(timeout_seconds=30.0),
        read_credentials(os.environ),
        DEFAULT_SETTINGS,
    )
    request = DownloadRequest(
        universe_path=UNIVERSE_CSV,
        bars_path=BARS_PARQUET,
        start=ten_years_before(today),
        end=today - timedelta(days=1),
    )
    print(render(download_bars(source, request)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
