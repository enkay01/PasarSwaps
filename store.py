"""The one Parquet file that holds the Dataset."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from bars import COLUMNS


@dataclass(frozen=True, slots=True)
class DatasetSpan:
    """What a Dataset holds: how many symbols, over which dates."""

    symbols: int
    first_date: date
    last_date: date


def dataset_span(frame: pd.DataFrame) -> DatasetSpan:
    """Summarise a Dataset frame by its symbol count and its date range."""
    return DatasetSpan(
        symbols=int(frame["symbol"].nunique()),
        first_date=frame["date"].min().date(),
        last_date=frame["date"].max().date(),
    )


def write_bars(path: Path, frame: pd.DataFrame) -> None:
    """Write the Dataset frame to one Parquet file, creating the folder if needed."""
    _require_columns(frame, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.loc[:, list(COLUMNS)].to_parquet(path, index=False)


def read_bars(path: Path) -> pd.DataFrame:
    """Read the whole Dataset back from one Parquet file."""
    if not path.is_file():
        raise FileNotFoundError(f"no Dataset at {path}; run download.py first")
    frame = pd.read_parquet(path)
    _require_columns(frame, path)
    if frame.empty:
        raise ValueError(f"Dataset at {path} holds no Bars")
    return frame


def _require_columns(frame: pd.DataFrame, path: Path) -> None:
    missing = [column for column in COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Dataset at {path} is missing columns: {', '.join(missing)}")
