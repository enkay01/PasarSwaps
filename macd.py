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


@dataclass(frozen=True, slots=True)
class SignalSeries:
    """Bullish and bearish cross flags over a symbol's history."""

    bullish: pd.Series
    bearish: pd.Series


def macd_histogram(adjusted_close: pd.Series) -> pd.Series:
    """The MACD histogram (MACD line minus signal line) on adjusted close."""
    fast = adjusted_close.astype("float64").ewm(span=FAST_SPAN, adjust=False).mean()
    slow = adjusted_close.astype("float64").ewm(span=SLOW_SPAN, adjust=False).mean()
    macd = fast - slow
    signal = macd.ewm(span=SIGNAL_SPAN, adjust=False).mean()
    return macd - signal


def macd_signals(history: pd.DataFrame) -> SignalSeries:
    """Compute bullish and bearish MACD crosses across history.

    A cross requires at least MINIMUM_BARS of history before producing a signal.
    A bullish cross occurs when the histogram is above zero and was at or below zero
    on the Bar before it. A bearish cross occurs when the histogram is below zero
    and was at or above zero on the Bar before it.
    """
    if len(history) < MINIMUM_BARS:
        empty = pd.Series(False, index=history.index)
        return SignalSeries(bullish=empty, bearish=empty)

    hist = macd_histogram(history["adjusted_close"])
    prev_hist = hist.shift(1)

    bull = (hist > 0) & (prev_hist <= 0)
    bear = (hist < 0) & (prev_hist >= 0)

    valid_mask = pd.Series(False, index=history.index)
    valid_mask.iloc[MINIMUM_BARS - 1 :] = True

    return SignalSeries(bullish=bull & valid_mask, bearish=bear & valid_mask)


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
        latest_bar = history.iloc[-1]
        if len(history) < MINIMUM_BARS or latest_bar["date"] != latest:
            continue
        if _crossed_on_latest_bar(history):
            crosses.append(
                Cross(
                    symbol=str(symbol),
                    date=latest_bar["date"].date(),
                    close=float(latest_bar["close"]),
                )
            )
    return crosses


def _crossed_on_latest_bar(history: pd.DataFrame) -> bool:
    signals = macd_signals(history)
    return bool(signals.bullish.iloc[-1])
