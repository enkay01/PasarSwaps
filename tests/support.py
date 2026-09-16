"""Small builders the tests share."""

from collections.abc import Sequence
from datetime import date, timedelta

from bars import Bar
from macd import MINIMUM_BARS

DAY_ZERO = date(2024, 1, 2)
FLAT_THEN_UP = [100.0] * (MINIMUM_BARS - 1) + [110.0]


def make_bar(
    symbol: str = "AAPL",
    day: date = DAY_ZERO,
    close: float = 100.0,
    adjusted_close: float = 100.0,
) -> Bar:
    """One Bar whose open, high and low match its close unless a test says otherwise."""
    return Bar(
        symbol=symbol,
        date=day,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1_000,
        adjusted_close=adjusted_close,
    )


def history(
    symbol: str,
    closes: Sequence[float],
    *,
    adjusted_closes: Sequence[float] | None = None,
) -> list[Bar]:
    """One Bar per close, one day apart, starting at DAY_ZERO."""
    adjusted = list(adjusted_closes) if adjusted_closes is not None else list(closes)
    return [
        make_bar(
            symbol=symbol,
            day=DAY_ZERO + timedelta(days=offset),
            close=close,
            adjusted_close=adjusted_close,
        )
        for offset, (close, adjusted_close) in enumerate(zip(closes, adjusted, strict=True))
    ]
