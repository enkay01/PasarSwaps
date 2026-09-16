"""The one Parquet file that holds the Dataset."""

from pathlib import Path

import pandas as pd

from bars import COLUMNS


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
