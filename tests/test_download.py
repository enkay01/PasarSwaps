"""The download command."""

from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

import pytest

from bars import Bar
from download import (
    DownloadRequest,
    DownloadSummary,
    download_bars,
    read_credentials,
    render,
    ten_years_before,
)
from store import read_bars
from support import DAY_ZERO, history

WINDOW_END = DAY_ZERO + timedelta(days=30)


class FakeSource:
    """A Source that hands back the Bars a test built, and records the ask."""

    def __init__(self, bars: Sequence[Bar]) -> None:
        self._bars = list(bars)
        self.asks: list[tuple[list[str], date, date]] = []

    def fetch_daily_bars(self, symbols: Sequence[str], start: date, end: date) -> list[Bar]:
        self.asks.append((list(symbols), start, end))
        return list(self._bars)


def write_universe(path: Path, symbols: Sequence[str]) -> Path:
    rows = "".join(f"{symbol},{symbol} Inc.\n" for symbol in symbols)
    path.write_text(f"Symbol,Security\n{rows}", encoding="utf-8")
    return path


def test_writes_the_dataset_and_reports_the_symbols_and_the_range(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", ["AAPL", "MSFT"])
    bars_path = tmp_path / "nested" / "bars.parquet"
    source = FakeSource([*history("AAPL", [100.0, 101.0]), *history("MSFT", [200.0, 201.0])])
    request = DownloadRequest(universe_path=universe, bars_path=bars_path, start=DAY_ZERO, end=WINDOW_END)

    summary = download_bars(source, request)

    assert summary.symbols == 2
    assert summary.first_date == DAY_ZERO
    assert summary.last_date == DAY_ZERO + timedelta(days=1)
    assert len(read_bars(bars_path)) == 4
    assert source.asks == [(["AAPL", "MSFT"], DAY_ZERO, WINDOW_END)]


def test_reads_the_two_credentials() -> None:
    credentials = read_credentials({"ALPACA_API_KEY": "key-id", "ALPACA_API_SECRET": "secret-key"})
    assert credentials.api_key == "key-id"
    assert credentials.api_secret == "secret-key"


def test_names_the_credential_that_is_missing() -> None:
    with pytest.raises(RuntimeError, match="ALPACA_API_SECRET"):
        read_credentials({"ALPACA_API_KEY": "key-id"})


def test_treats_a_blank_credential_as_missing() -> None:
    with pytest.raises(RuntimeError, match="ALPACA_API_KEY"):
        read_credentials({"ALPACA_API_KEY": "  ", "ALPACA_API_SECRET": "secret-key"})


def test_ten_years_before_moves_a_leap_day_to_february_28() -> None:
    assert ten_years_before(date(2024, 2, 29)) == date(2014, 2, 28)


def test_ten_years_before_keeps_an_ordinary_day() -> None:
    assert ten_years_before(date(2026, 9, 16)) == date(2016, 9, 16)


def test_render_prints_the_count_and_the_range() -> None:
    summary = DownloadSummary(symbols=503, first_date=date(2016, 9, 16), last_date=date(2026, 9, 15))
    assert render(summary) == "wrote 503 symbols, 2016-09-16 to 2026-09-15"
