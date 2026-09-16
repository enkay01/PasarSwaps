"""The screen command."""

from datetime import date, timedelta
from pathlib import Path

from bars import bars_to_frame
from macd import MINIMUM_BARS, Cross
from screen import ScreenResult, render, run_screen
from store import write_bars
from support import DAY_ZERO, history

FLAT_THEN_UP = [100.0] * (MINIMUM_BARS - 1) + [110.0]
SCREEN_DATE = DAY_ZERO + timedelta(days=MINIMUM_BARS - 1)


def test_reads_the_dataset_and_reports_the_crosses(tmp_path: Path) -> None:
    frame = bars_to_frame([*history("AAPL", FLAT_THEN_UP), *history("MSFT", [200.0] * MINIMUM_BARS)])
    bars_path = tmp_path / "bars.parquet"
    write_bars(bars_path, frame)

    result = run_screen(bars_path)

    assert result.as_of == SCREEN_DATE
    assert result.symbols_read == 2
    assert [cross.symbol for cross in result.crosses] == ["AAPL"]


def test_render_prints_one_line_per_cross_then_the_count() -> None:
    result = ScreenResult(
        as_of=date(2026, 9, 15),
        crosses=[Cross(symbol="AAPL", date=date(2026, 9, 15), close=231.45)],
        symbols_read=503,
    )
    assert render(result) == "\n".join(
        [
            "S&P 500 MACD screen on the Bar for 2026-09-15",
            "symbol  date        close",
            "AAPL    2026-09-15  231.45",
            "crosses: 1",
            "symbols read: 503",
        ]
    )


def test_render_prints_the_counts_when_nothing_crossed() -> None:
    result = ScreenResult(as_of=date(2026, 9, 15), crosses=[], symbols_read=503)
    assert render(result) == "\n".join(
        [
            "S&P 500 MACD screen on the Bar for 2026-09-15",
            "symbol  date        close",
            "crosses: 0",
            "symbols read: 503",
        ]
    )
