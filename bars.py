"""The Bar record that crosses the Source seam, and the frame it is stored in."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol

import pandas as pd

COLUMNS: tuple[str, ...] = (
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "adjusted_close",
)


@dataclass(frozen=True, slots=True)
class Bar:
    """One daily price interval for one symbol, raw and adjusted."""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float


class BarSource(Protocol):
    """A Source that returns daily Bars for a whole symbol list."""

    def fetch_daily_bars(self, symbols: Sequence[str], start: date, end: date) -> list[Bar]:
        """Return every daily Bar for the symbols between the two dates."""
        ...


def bars_to_frame(bars: Sequence[Bar]) -> pd.DataFrame:
    """Lay the Bars out as the Dataset frame, in the stored column order."""
    frame = pd.DataFrame(
        {
            "symbol": [bar.symbol for bar in bars],
            "date": [bar.date for bar in bars],
            "open": [bar.open for bar in bars],
            "high": [bar.high for bar in bars],
            "low": [bar.low for bar in bars],
            "close": [bar.close for bar in bars],
            "volume": [bar.volume for bar in bars],
            "adjusted_close": [bar.adjusted_close for bar in bars],
        }
    )
    return frame.loc[:, list(COLUMNS)].astype({"date": "datetime64[ns]", "volume": "int64"})
