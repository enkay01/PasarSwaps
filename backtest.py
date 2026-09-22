"""Backtest the MACD cross strategy over the S&P 500 Dataset.

    python backtest.py

Reads data/sp500_daily_bars.parquet and prints the return, the Fill count,
and the settings the run used.
"""

from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd

from macd import macd_signals
from paths import BARS_PARQUET
from store import read_bars


@dataclass(frozen=True, slots=True)
class BacktestSettings:
    """The settings for one Backtest run."""

    starting_cash: float = 100_000.0
    slippage_bps: int = 0


DEFAULT_SETTINGS = BacktestSettings()


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """The outcome of one Backtest run over the Dataset."""

    starting_cash: float
    final_equity: float
    total_return: float
    fill_count: int
    slippage_bps: int


@dataclass(frozen=True, slots=True)
class _DailyBar:
    adj_open: float
    adj_close: float
    bullish: bool
    bearish: bool


def evaluate_backtest(
    frame: pd.DataFrame,
    settings: BacktestSettings = DEFAULT_SETTINGS,
) -> BacktestResult:
    """Run the MACD trading rules over a Dataset frame."""
    if frame.empty:
        return BacktestResult(
            starting_cash=settings.starting_cash,
            final_equity=settings.starting_cash,
            total_return=0.0,
            fill_count=0,
            slippage_bps=settings.slippage_bps,
        )

    slippage_rate = settings.slippage_bps / 10_000.0
    universe_size = int(frame["symbol"].nunique())

    # Precalculate signals and adjusted prices per symbol
    bars_by_date: dict[object, dict[str, _DailyBar]] = {}
    for symbol, group in frame.groupby("symbol", sort=True):
        history = group.sort_values("date").reset_index(drop=True)
        signals = macd_signals(history)
        close_series = history["close"].astype("float64")
        adj_close_series = history["adjusted_close"].astype("float64")
        open_series = history["open"].astype("float64")

        ratio = adj_close_series / close_series
        adj_open_series = open_series * ratio

        dates = history["date"].values
        adj_opens = adj_open_series.values
        adj_closes = adj_close_series.values
        bulls = signals.bullish.values
        bears = signals.bearish.values

        for d, o, c, bull, bear in zip(dates, adj_opens, adj_closes, bulls, bears, strict=True):
            if d not in bars_by_date:
                bars_by_date[d] = {}
            bars_by_date[d][str(symbol)] = _DailyBar(
                adj_open=float(o),
                adj_close=float(c),
                bullish=bool(bull),
                bearish=bool(bear),
            )

    sorted_dates = sorted(bars_by_date.keys())

    cash = settings.starting_cash
    positions: dict[str, float] = {}
    open_prices: dict[str, float] = {}
    close_prices: dict[str, float] = {}
    pending_entries: set[str] = set()
    pending_exits: set[str] = set()
    fill_count = 0

    for d in sorted_dates:
        today = bars_by_date[d]
        for sym, bar in today.items():
            open_prices[sym] = bar.adj_open
            close_prices[sym] = bar.adj_close

        # 1. Process exits at the open
        for sym in sorted(pending_exits):
            if sym in today and sym in positions:
                exit_price = today[sym].adj_open * (1.0 - slippage_rate)
                shares = positions.pop(sym)
                cash += shares * exit_price
                fill_count += 1
        pending_exits = {sym for sym in pending_exits if sym in positions}

        # 2. Process entries at the open
        eligible = [
            sym
            for sym in sorted(pending_entries)
            if sym in today and sym not in positions and today[sym].adj_open > 0
        ]
        if eligible and cash > 0:
            open_val = sum(shares * open_prices.get(sym, 0.0) for sym, shares in positions.items())
            equity = cash + open_val
            target_alloc = equity / universe_size
            cash_per_symbol = cash / len(eligible)
            alloc = min(target_alloc, cash_per_symbol)
            if alloc > 0:
                for sym in eligible:
                    entry_price = today[sym].adj_open * (1.0 + slippage_rate)
                    if entry_price > 0 and cash >= alloc:
                        positions[sym] = alloc / entry_price
                        cash -= alloc
                        fill_count += 1
        pending_entries.clear()

        # 3. Evaluate signals at the close
        for sym, bar in today.items():
            if bar.bullish and sym not in positions:
                pending_entries.add(sym)
            if bar.bearish and sym in positions:
                pending_exits.add(sym)

    # Final valuation of open positions at last available adjusted close
    final_pos_val = sum(shares * close_prices.get(sym, 0.0) for sym, shares in positions.items())
    final_equity = cash + final_pos_val
    total_return = (final_equity - settings.starting_cash) / settings.starting_cash

    return BacktestResult(
        starting_cash=settings.starting_cash,
        final_equity=final_equity,
        total_return=total_return,
        fill_count=fill_count,
        slippage_bps=settings.slippage_bps,
    )


def run_backtest(
    bars_path: Path,
    settings: BacktestSettings = DEFAULT_SETTINGS,
) -> BacktestResult:
    """Run the MACD Backtest over the Dataset on disk."""
    frame = read_bars(bars_path)
    return evaluate_backtest(frame, settings)


def render(result: BacktestResult) -> str:
    """The block the run prints: return, fill count and settings."""
    lines = [
        "S&P 500 MACD backtest",
        f"return: {result.total_return * 100:.2f}%",
        f"fill count: {result.fill_count}",
        f"starting cash: USD {result.starting_cash:,.2f}",
        f"slippage: {result.slippage_bps} bps",
    ]
    return "\n".join(lines)


def main() -> int:
    """Read the Dataset and print the Backtest result."""
    result = run_backtest(BARS_PARQUET)
    print(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
