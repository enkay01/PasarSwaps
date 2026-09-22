"""The MACD rules the Screen runs."""

from datetime import timedelta

from bars import bars_to_frame
from macd import MINIMUM_BARS, fresh_bullish_crosses, macd_signals
from support import DAY_ZERO, FLAT_THEN_UP, history


def test_reports_a_symbol_that_crosses_up_on_the_latest_bar() -> None:
    frame = bars_to_frame(history("AAPL", FLAT_THEN_UP))
    crosses = fresh_bullish_crosses(frame)
    assert [cross.symbol for cross in crosses] == ["AAPL"]
    assert crosses[0].date == DAY_ZERO + timedelta(days=MINIMUM_BARS - 1)
    assert crosses[0].close == 110.0


def test_reads_the_cross_from_the_adjusted_close() -> None:
    frame = bars_to_frame(
        history("AAPL", [100.0] * MINIMUM_BARS, adjusted_closes=FLAT_THEN_UP),
    )
    assert [cross.symbol for cross in fresh_bullish_crosses(frame)] == ["AAPL"]


def test_ignores_a_raw_close_that_moves_while_the_adjusted_close_does_not() -> None:
    frame = bars_to_frame(
        history("AAPL", [100.0] * (MINIMUM_BARS - 1) + [400.0], adjusted_closes=[100.0] * MINIMUM_BARS),
    )
    assert fresh_bullish_crosses(frame) == []


def test_ignores_a_symbol_whose_latest_bar_is_before_the_screen_date() -> None:
    stale = history("AAPL", FLAT_THEN_UP)[:-1]
    frame = bars_to_frame([*history("MSFT", FLAT_THEN_UP), *stale])
    assert [cross.symbol for cross in fresh_bullish_crosses(frame)] == ["MSFT"]


def test_ignores_a_symbol_with_too_little_history() -> None:
    frame = bars_to_frame(history("AAPL", FLAT_THEN_UP[: MINIMUM_BARS - 1]))
    assert fresh_bullish_crosses(frame) == []


def test_ignores_a_symbol_that_falls_on_the_latest_bar() -> None:
    frame = bars_to_frame(history("AAPL", [100.0] * (MINIMUM_BARS - 1) + [90.0]))
    assert fresh_bullish_crosses(frame) == []


def test_ignores_a_cross_from_an_earlier_bar() -> None:
    frame = bars_to_frame(history("AAPL", [100.0] * (MINIMUM_BARS - 2) + [110.0, 111.0]))
    assert fresh_bullish_crosses(frame) == []


def test_returns_the_crosses_in_symbol_order() -> None:
    frame = bars_to_frame([*history("ZZZ", FLAT_THEN_UP), *history("AAA", FLAT_THEN_UP)])
    assert [cross.symbol for cross in fresh_bullish_crosses(frame)] == ["AAA", "ZZZ"]


def test_reports_nothing_for_an_empty_frame() -> None:
    assert fresh_bullish_crosses(bars_to_frame([])) == []


def test_macd_signals_identifies_bullish_and_bearish_crosses() -> None:
    # 34 flat bars, then 10 up bars (bullish cross), then 10 down bars (bearish cross)
    closes = [100.0] * (MINIMUM_BARS - 1) + [110.0] * 10 + [90.0] * 10
    frame = bars_to_frame(history("AAPL", closes))
    signals = macd_signals(frame)

    assert signals.bullish.iloc[MINIMUM_BARS - 1]
    assert not signals.bearish.iloc[MINIMUM_BARS - 1]
    # In the downward stretch, a bearish cross should occur
    assert signals.bearish.any()


def test_macd_signals_returns_empty_when_under_minimum_bars() -> None:
    frame = bars_to_frame(history("AAPL", [100.0] * (MINIMUM_BARS - 1)))
    signals = macd_signals(frame)
    assert not signals.bullish.any()
    assert not signals.bearish.any()
