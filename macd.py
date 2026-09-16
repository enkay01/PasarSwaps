"""The MACD rules the Screen runs over the latest Bar of the Dataset."""

from dataclasses import dataclass
from datetime import date

import pandas as pd

FAST_SPAN = 12
SLOW_SPAN = 26
SIGNAL_SPAN = 9
MINIMUM_BARS = SLOW_SPAN + SIGNAL_SPAN


@dataclass(frozen=True, slots=True)
class Cross:
    """A symbol whose MACD line crossed above its signal line on one Bar."""

    symbol: str
    date: date
    close: float


def fresh_bullish_crosses(bars: pd.DataFrame) -> list[Cross]:
    """Return the symbols with a fresh bullish MACD cross on the latest Bar.

    MACD runs on the adjusted close, because a split inside the window invents a
    cross that never happened. The cross is fresh when the histogram is above zero
    on the latest Bar and was at or below zero on the Bar before it.
    """
    latest = bars["date"].max()
    crosses: list[Cross] = []
    for symbol, history in bars.groupby("symbol", sort=True):
        history = history.sort_values("date").reset_index(drop=True)
        if len(history) < MINIMUM_BARS or history["date"].iloc[-1] != latest:
            continue
        if _crossed_on_latest_bar(history):
            crosses.append(
                Cross(
                    symbol=str(symbol),
                    date=history["date"].iloc[-1].date(),
                    close=float(history["close"].iloc[-1]),
                )
            )
    return crosses


def _crossed_on_latest_bar(history: pd.DataFrame) -> bool:
    adjusted_close = history["adjusted_close"].astype("float64")
    fast = adjusted_close.ewm(span=FAST_SPAN, adjust=False).mean()
    slow = adjusted_close.ewm(span=SLOW_SPAN, adjust=False).mean()
    macd = fast - slow
    signal = macd.ewm(span=SIGNAL_SPAN, adjust=False).mean()
    histogram = macd - signal
    return bool(histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0)
