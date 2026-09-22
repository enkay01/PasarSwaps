"""The backtest command and evaluation rules."""

from datetime import date, timedelta
from pathlib import Path

from backtest import BacktestResult, BacktestSettings, evaluate_backtest, render, run_backtest
from bars import Bar, bars_to_frame
from macd import MINIMUM_BARS
from store import write_bars
from support import DAY_ZERO, make_bar


def test_empty_dataset_returns_zero_return_and_zero_fills() -> None:
    frame = bars_to_frame([])
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0))

    assert result.starting_cash == 100_000.0
    assert result.final_equity == 100_000.0
    assert result.total_return == 0.0
    assert result.fill_count == 0


def test_single_symbol_entry_and_exit_cycle() -> None:
    # 34 flat bars (100.0), 1 bar at 110.0 (bullish cross at bar 35).
    # Bar 36: entry fills at open (110.0). Price stays 110.0.
    # Bar 37: price drops to 80.0 (bearish cross at close of bar 37).
    # Bar 38: exit fills at open (80.0).
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS - 1):
        bars.append(make_bar("AAPL", current_day, close=100.0, adjusted_close=100.0))
        current_day += timedelta(days=1)

    # Bullish cross at close
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    current_day += timedelta(days=1)

    # Day of entry fill at open
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    current_day += timedelta(days=1)

    # Bearish cross at close
    bars.append(make_bar("AAPL", current_day, close=80.0, adjusted_close=80.0))
    current_day += timedelta(days=1)

    # Day of exit fill at open
    bars.append(make_bar("AAPL", current_day, close=80.0, adjusted_close=80.0))

    frame = bars_to_frame(bars)
    settings = BacktestSettings(starting_cash=100_000.0, slippage_bps=0)
    result = evaluate_backtest(frame, settings)

    # 1 entry fill and 1 exit fill
    assert result.fill_count == 2
    # Entire cash invested (1 symbol in universe -> 100% of equity allocated)
    # Buy at 110.0, sell at 80.0 -> loss of (80 - 110) / 110 = -27.2727...%
    expected_shares = 100_000.0 / 110.0
    expected_cash = expected_shares * 80.0
    assert round(result.final_equity, 2) == round(expected_cash, 2)
    assert round(result.total_return, 4) == round((expected_cash - 100_000.0) / 100_000.0, 4)


def test_position_valued_at_last_bar_adjusted_close_when_held_open() -> None:
    # Bullish cross occurs, enters on next bar open, and stays held without an exit signal
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS - 1):
        bars.append(make_bar("AAPL", current_day, close=100.0, adjusted_close=100.0))
        current_day += timedelta(days=1)

    # Bullish cross at close
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    current_day += timedelta(days=1)

    # Entry fills at open 110.0, closes at 120.0 (last bar)
    bars.append(
        Bar(
            symbol="AAPL",
            date=current_day,
            open=110.0,
            high=125.0,
            low=110.0,
            close=120.0,
            volume=1_000,
            adjusted_close=120.0,
        )
    )

    frame = bars_to_frame(bars)
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))

    # Only 1 fill (the entry)
    assert result.fill_count == 1
    # Valued at final adjusted close 120.0
    shares = 100_000.0 / 110.0
    expected_equity = shares * 120.0
    assert round(result.final_equity, 2) == round(expected_equity, 2)


def test_fills_use_adjusted_open_so_splits_do_not_invent_losses() -> None:
    # 4-for-1 split scenario: raw price falls from 400 to 100, but adjusted series is flat.
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS - 1):
        bars.append(make_bar("AAPL", current_day, close=400.0, adjusted_close=100.0))
        current_day += timedelta(days=1)

    # Bullish cross on adjusted close
    bars.append(make_bar("AAPL", current_day, close=440.0, adjusted_close=110.0))
    current_day += timedelta(days=1)

    # Entry bar: stock split occurs here. Raw open = 110.0, raw close = 110.0, adjusted close = 110.0.
    # Adjusted open = 110.0 * (110.0 / 110.0) = 110.0.
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))

    frame = bars_to_frame(bars)
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))

    assert result.fill_count == 1
    # Bought at adjusted open 110.0, valued at final adjusted close 110.0 -> 0% return
    assert round(result.total_return, 4) == 0.0


def test_slippage_reduces_returns() -> None:
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS - 1):
        bars.append(make_bar("AAPL", current_day, close=100.0, adjusted_close=100.0))
        current_day += timedelta(days=1)

    # Bullish cross
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    current_day += timedelta(days=1)

    # Entry fills at open 110.0, close 120.0
    bars.append(make_bar("AAPL", current_day, close=120.0, adjusted_close=120.0))

    frame = bars_to_frame(bars)

    no_slippage = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))
    with_slippage = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=50))

    # With 50 bps slippage, buy price is higher (110 * 1.005), so fewer shares bought
    assert with_slippage.final_equity < no_slippage.final_equity
    assert with_slippage.total_return < no_slippage.total_return


def test_cash_allocation_shares_equity_across_universe() -> None:
    # 2 symbols in universe: AAPL and MSFT.
    # When AAPL enters, target allocation is equity / 2 (50% of equity).
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS - 1):
        bars.append(make_bar("AAPL", current_day, close=100.0, adjusted_close=100.0))
        bars.append(make_bar("MSFT", current_day, close=200.0, adjusted_close=200.0))
        current_day += timedelta(days=1)

    # AAPL crosses bullishly, MSFT remains flat
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    bars.append(make_bar("MSFT", current_day, close=200.0, adjusted_close=200.0))
    current_day += timedelta(days=1)

    # AAPL enters at open 110.0. MSFT stays flat.
    bars.append(make_bar("AAPL", current_day, close=110.0, adjusted_close=110.0))
    bars.append(make_bar("MSFT", current_day, close=200.0, adjusted_close=200.0))

    frame = bars_to_frame(bars)
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))

    assert result.fill_count == 1
    # 50,000 allocated (half of 100,000 equity)
    shares = 50_000.0 / 110.0
    expected_equity = 50_000.0 + (shares * 110.0)
    assert round(result.final_equity, 2) == round(expected_equity, 2)


def test_render_formats_expected_output() -> None:
    result = BacktestResult(
        starting_cash=100_000.0,
        final_equity=151_600.0,
        total_return=0.516,
        fill_count=58455,
        slippage_bps=0,
    )
    expected = "\n".join(
        [
            "S&P 500 MACD backtest",
            "return: 51.60%",
            "fill count: 58455",
            "starting cash: USD 100,000.00",
            "slippage: 0 bps",
        ]
    )
    assert render(result) == expected


def test_run_backtest_reads_dataset_from_disk(tmp_path: Path) -> None:
    bars: list[Bar] = []
    current_day = DAY_ZERO
    for _ in range(MINIMUM_BARS):
        bars.append(make_bar("AAPL", current_day, close=100.0, adjusted_close=100.0))
        current_day += timedelta(days=1)

    frame = bars_to_frame(bars)
    parquet_path = tmp_path / "bars.parquet"
    write_bars(parquet_path, frame)

    result = run_backtest(parquet_path, BacktestSettings(starting_cash=100_000.0))
    assert result.fill_count == 0
    assert result.total_return == 0.0
