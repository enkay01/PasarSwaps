"""Backtest the MACD cross strategy over the S&P 500 Dataset.

    python backtest.py

Reads data/sp500_daily_bars.parquet and prints the return and the Fill count
alongside the settings.
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
    """The settings for one Backtest."""

    starting_cash: float = 100_000.0
    commission: float = 0.0
    slippage_bps: int = 0


DEFAULT_SETTINGS = BacktestSettings()


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """The outcome of one Backtest over the Dataset."""

    starting_cash: float
    ending_cash: float
    final_equity: float
    total_return: float
    fill_count: int
    commission: float
    slippage_bps: int


@dataclass(frozen=True, slots=True)
class _DailyBar:
    adjusted_open: float
    adjusted_close: float
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
            ending_cash=settings.starting_cash,
            final_equity=settings.starting_cash,
            total_return=0.0,
            fill_count=0,
            commission=settings.commission,
            slippage_bps=settings.slippage_bps,
        )

    slippage_rate = settings.slippage_bps / 10_000.0
    universe_size = int(frame["symbol"].nunique())

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
        open_vals = adj_open_series.values
        close_vals = adj_close_series.values
        bull_vals = signals.bullish.values
        bear_vals = signals.bearish.values

        for bar_date, open_val, close_val, bull_val, bear_val in zip(
            dates, open_vals, close_vals, bull_vals, bear_vals, strict=True
        ):
            if bar_date not in bars_by_date:
                bars_by_date[bar_date] = {}
            bars_by_date[bar_date][str(symbol)] = _DailyBar(
                adjusted_open=float(open_val),
                adjusted_close=float(close_val),
                bullish=bool(bull_val),
                bearish=bool(bear_val),
            )

    sorted_dates = sorted(bars_by_date.keys())

    cash = settings.starting_cash
    positions: dict[str, float] = {}
    open_prices: dict[str, float] = {}
    close_prices: dict[str, float] = {}
    pending_entries: set[str] = set()
    pending_exits: set[str] = set()
    fill_count = 0

    for bar_date in sorted_dates:
        today = bars_by_date[bar_date]
        for sym, bar in today.items():
            open_prices[sym] = bar.adjusted_open
            close_prices[sym] = bar.adjusted_close

        # 1. Process exits at the open
        for sym in sorted(pending_exits):
            if sym in today and sym in positions:
                exit_price = today[sym].adjusted_open * (1.0 - slippage_rate)
                shares = positions.pop(sym)
                cash += (shares * exit_price) - settings.commission
                fill_count += 1
        pending_exits = {sym for sym in pending_exits if sym in positions and sym not in today}

        # 2. Process entries at the open
        eligible = [
            sym
            for sym in sorted(pending_entries)
            if sym in today and sym not in positions and today[sym].adjusted_open > 0
        ]
        if eligible and cash > 0:
            open_val = sum(shares * open_prices.get(sym, 0.0) for sym, shares in positions.items())
            equity = cash + open_val
            target_alloc = equity / universe_size
            cash_per_symbol = cash / len(eligible)
            alloc = min(target_alloc, cash_per_symbol)
            if alloc > 0:
                for sym in eligible:
                    entry_price = today[sym].adjusted_open * (1.0 + slippage_rate)
                    trade_cash = min(alloc, cash)
                    if entry_price > 0 and trade_cash > settings.commission:
                        effective_capital = trade_cash - settings.commission
                        positions[sym] = effective_capital / entry_price
                        cash -= trade_cash
                        cash = max(0.0, cash)
                        fill_count += 1
        pending_entries = {sym for sym in pending_entries if sym not in today and sym not in positions}

        # 3. Evaluate signals at the close
        for sym, bar in today.items():
            if bar.bullish and sym not in positions:
                pending_entries.add(sym)
            if bar.bearish and sym in positions:
                pending_exits.add(sym)

    final_pos_val = sum(shares * close_prices.get(sym, 0.0) for sym, shares in positions.items())
    final_equity = cash + final_pos_val
    total_return = (final_equity - settings.starting_cash) / settings.starting_cash

    return BacktestResult(
        starting_cash=settings.starting_cash,
        ending_cash=cash,
        final_equity=final_equity,
        total_return=total_return,
        fill_count=fill_count,
        commission=settings.commission,
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
    """The block the Backtest prints."""
    lines = [
        "S&P 500 MACD backtest",
        f"return: {result.total_return * 100:.2f}%",
        f"fill count: {result.fill_count}",
        f"starting cash: USD {result.starting_cash:,.2f}",
        f"ending cash: USD {result.ending_cash:,.2f}",
        f"commission: USD {result.commission:.2f}",
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
