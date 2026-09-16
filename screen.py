"""Print the S&P 500 symbols with a fresh bullish MACD cross on the latest Bar.

    python screen.py

Reads data/sp500_daily_bars.parquet and never touches the network.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import sys

from macd import Cross, fresh_bullish_crosses
from paths import BARS_PARQUET
from store import dataset_span, read_bars


@dataclass(frozen=True, slots=True)
class ScreenResult:
    """The Bar the Screen ran on, the crosses it found, and how much it read."""

    screen_date: date
    crosses: list[Cross]
    symbols_read: int


def run_screen(bars_path: Path) -> ScreenResult:
    """Run the MACD rules over the Dataset on disk."""
    frame = read_bars(bars_path)
    span = dataset_span(frame)
    return ScreenResult(
        screen_date=span.last_date,
        crosses=fresh_bullish_crosses(frame),
        symbols_read=span.symbols,
    )


def render(result: ScreenResult) -> str:
    """The block the run prints: one line per cross, then the symbol count."""
    lines = [
        f"S&P 500 MACD screen on the Bar for {result.screen_date}",
        f"{'symbol':<8}{'date':<12}close",
        *(f"{cross.symbol:<8}{cross.date!s:<12}{cross.close:.2f}" for cross in result.crosses),
        f"crosses: {len(result.crosses)}",
        f"symbols read: {result.symbols_read}",
    ]
    return "\n".join(lines)


def main() -> int:
    """Read the Dataset and print the crosses."""
    print(render(run_screen(BARS_PARQUET)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
