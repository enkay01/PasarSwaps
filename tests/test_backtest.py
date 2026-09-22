"""The backtest command and evaluation rules."""

from datetime import date, timedelta
from pathlib import Path

from backtest import BacktestResult, BacktestSettings, evaluate_backtest, render, run_backtest
from bars import Bar, bars_to_frame
from macd import MINIMUM_BARS
from store import write_bars
from support import DAY_ZERO, history, make_bar


def test_empty_dataset_returns_zero_return_and_zero_fills() -> None:
    frame = bars_to_frame([])
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0))

    assert result.starting_cash == 100_000.0
    assert result.ending_cash == 100_000.0
    assert result.invested_sum == 0.0
    assert result.final_equity == 100_000.0
    assert result.total_return == 0.0
    assert result.fill_count == 0
    assert result.commission == 0.0


def test_single_symbol_entry_and_exit_cycle() -> None:
    # 34 flat bars (100.0), 1 bar at 110.0 (bullish cross at bar 35).
    # Bar 36: entry fills at open (110.0). Price stays 110.0.
    # Bar 37: price drops to 80.0 (bearish cross at close of bar 37).
    # Bar 38: exit fills at open (80.0).
    closes = [100.0] * (MINIMUM_BARS - 1) + [110.0, 110.0, 80.0, 80.0]
    frame = bars_to_frame(history("AAPL", closes))
    settings = BacktestSettings(starting_cash=100_000.0, slippage_bps=0)
    result = evaluate_backtest(frame, settings)

    assert result.fill_count == 2
    expected_shares = 100_000.0 / 110.0
    expected_cash = expected_shares * 80.0
    assert round(result.final_equity, 2) == round(expected_cash, 2)
    assert round(result.total_return, 4) == round((expected_cash - 100_000.0) / 100_000.0, 4)


def test_position_valued_at_last_bar_adjusted_close_when_held_open() -> None:
    # 34 flat bars, 1 bar at 110.0 (bullish cross), then entry at open 110.0 closing at 120.0
    bars = history("AAPL", [100.0] * (MINIMUM_BARS - 1) + [110.0])
    last_day = bars[-1].date + timedelta(days=1)
    bars.append(
        Bar(
            symbol="AAPL",
            date=last_day,
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

    assert result.fill_count == 1
    shares = 100_000.0 / 110.0
    expected_equity = shares * 120.0
    assert result.ending_cash == 0.0
    assert round(result.invested_sum, 2) == round(expected_equity, 2)
    assert round(result.final_equity, 2) == round(expected_equity, 2)


def test_fills_use_adjusted_open_so_splits_do_not_invent_losses() -> None:
    # 2-for-1 split scenario: raw price is double adjusted price across the history,
    # including on the fill bar where raw open is 200.0 while adjusted open is 100.0.
    adjusted = [100.0] * (MINIMUM_BARS - 1) + [110.0, 100.0]
    raw = [200.0] * (MINIMUM_BARS - 1) + [220.0, 200.0]
    frame = bars_to_frame(history("AAPL", raw, adjusted_closes=adjusted))
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))

    assert result.fill_count == 1
    assert result.ending_cash == 0.0
    assert result.invested_sum == 100_000.0
    assert result.final_equity == 100_000.0
    assert round(result.total_return, 4) == 0.0


def test_slippage_reduces_returns() -> None:
    closes = [100.0] * (MINIMUM_BARS - 1) + [110.0, 120.0]
    frame = bars_to_frame(history("AAPL", closes))

    no_slippage = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))
    with_slippage = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=50))

    assert with_slippage.final_equity < no_slippage.final_equity
    assert with_slippage.total_return < no_slippage.total_return


def test_cash_allocation_shares_equity_across_universe() -> None:
    aapl_closes = [100.0] * (MINIMUM_BARS - 1) + [110.0, 110.0]
    msft_closes = [200.0] * (MINIMUM_BARS + 1)
    frame = bars_to_frame([*history("AAPL", aapl_closes), *history("MSFT", msft_closes)])
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0, slippage_bps=0))

    assert result.fill_count == 1
    assert result.ending_cash == 50_000.0
    shares = 50_000.0 / 110.0
    expected_invested = shares * 110.0
    assert round(result.invested_sum, 2) == round(expected_invested, 2)
    assert round(result.final_equity, 2) == 100_000.0


def test_entry_executes_on_symbol_next_bar_even_with_calendar_gap() -> None:
    # AAPL crosses on day T, but has no Bar on day T+1 (other symbols trade).
    # AAPL trades on day T+2; the entry fill must execute on day T+2.
    aapl_bars = history("AAPL", [100.0] * (MINIMUM_BARS - 1) + [110.0])
    cross_date = aapl_bars[-1].date
    # MSFT trades on day T+1
    msft_bars = history("MSFT", [200.0] * (MINIMUM_BARS + 1))
    # AAPL skips day T+1 and appears on day T+2
    aapl_bars.append(make_bar("AAPL", cross_date + timedelta(days=2), close=110.0, adjusted_close=110.0))

    frame = bars_to_frame([*aapl_bars, *msft_bars])
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0))

    assert result.fill_count == 1


def test_precision_loss_does_not_drop_eligible_symbols() -> None:
    # 3 symbols cross on the same bar with 100.0 total cash
    syms = ["AAA", "BBB", "CCC"]
    bars: list[Bar] = []
    for sym in syms:
        bars.extend(history(sym, [100.0] * (MINIMUM_BARS - 1) + [110.0, 110.0]))

    frame = bars_to_frame(bars)
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100.0))

    assert result.fill_count == 3


def test_render_formats_expected_output() -> None:
    result = BacktestResult(
        starting_cash=100_000.0,
        ending_cash=115_214.74,
        invested_sum=36_385.26,
        final_equity=151_600.0,
        total_return=0.516,
        fill_count=58455,
        commission=0.0,
        slippage_bps=0,
    )
    expected = "\n".join(
        [
            "S&P 500 MACD backtest",
            "return: 51.60%",
            "fill count: 58455",
            "starting cash: USD 100,000.00",
            "ending cash: USD 115,214.74",
            "invested sum: USD 36,385.26",
            "final equity: USD 151,600.00",
            "commission: USD 0.00",
            "slippage: 0 bps",
        ]
    )
    assert render(result) == expected


def test_run_backtest_reads_dataset_from_disk(tmp_path: Path) -> None:
    frame = bars_to_frame(history("AAPL", [100.0] * MINIMUM_BARS))
    parquet_path = tmp_path / "bars.parquet"
    write_bars(parquet_path, frame)

    result = run_backtest(parquet_path, BacktestSettings(starting_cash=100_000.0))
    assert result.fill_count == 0
    assert result.total_return == 0.0


def test_starting_cash_zero_returns_zero_return() -> None:
    frame = bars_to_frame([])
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=0.0))

    assert result.starting_cash == 0.0
    assert result.final_equity == 0.0
    assert result.total_return == 0.0


def test_zero_close_produces_zero_adjusted_open_and_avoids_crash() -> None:
    bars = history("AAPL", [100.0] * (MINIMUM_BARS - 1) + [110.0])
    last_day = bars[-1].date + timedelta(days=1)
    bars.append(
        Bar(
            symbol="AAPL",
            date=last_day,
            open=100.0,
            high=100.0,
            low=0.0,
            close=0.0,
            volume=1_000,
            adjusted_close=0.0,
        )
    )
    frame = bars_to_frame(bars)
    result = evaluate_backtest(frame, BacktestSettings(starting_cash=100_000.0))

    assert result.fill_count == 0
    assert result.final_equity == 100_000.0


def test_exit_commission_does_not_drive_cash_negative() -> None:
    closes = [100.0] * (MINIMUM_BARS - 1) + [110.0, 110.0, 80.0, 80.0]
    frame = bars_to_frame(history("AAPL", closes))
    settings = BacktestSettings(starting_cash=100.0, commission=50.0, slippage_bps=0)
    result = evaluate_backtest(frame, settings)

    assert result.fill_count == 2
    assert result.ending_cash == 0.0
    assert result.final_equity == 0.0
