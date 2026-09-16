"""The Universe: the S&P 500 symbol list from the static CSV in the repository."""

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

SYMBOL_COLUMN = "Symbol"


def read_universe(path: Path) -> list[str]:
    """Return the symbols of the Universe in file order, without duplicates."""
    if not path.is_file():
        raise FileNotFoundError(f"no Universe file at {path}")
    frame = pd.read_csv(path)
    if SYMBOL_COLUMN not in frame.columns:
        raise ValueError(f"Universe file at {path} has no {SYMBOL_COLUMN} column")
    symbols = _without_duplicates(frame[SYMBOL_COLUMN].dropna().astype(str).str.strip())
    if not symbols:
        raise ValueError(f"Universe file at {path} holds no symbols")
    return symbols


def _without_duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered
