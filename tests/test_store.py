"""The one Parquet file that holds the Dataset."""

from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from bars import bars_to_frame
from store import read_bars, write_bars
from support import make_bar


def test_round_trips_the_frame(tmp_path: Path) -> None:
    frame = bars_to_frame([make_bar(symbol="AAPL"), make_bar(symbol="MSFT", close=200.0)])
    bars_path = tmp_path / "bars.parquet"
    write_bars(bars_path, frame)
    assert_frame_equal(read_bars(bars_path), frame)


def test_creates_the_folder_it_writes_into(tmp_path: Path) -> None:
    bars_path = tmp_path / "nested" / "bars.parquet"
    write_bars(bars_path, bars_to_frame([make_bar()]))
    assert bars_path.is_file()


def test_rejects_a_frame_missing_a_column(tmp_path: Path) -> None:
    frame = bars_to_frame([make_bar()]).drop(columns=["adjusted_close"])
    with pytest.raises(ValueError, match="adjusted_close"):
        write_bars(tmp_path / "bars.parquet", frame)


def test_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="run download.py"):
        read_bars(tmp_path / "absent.parquet")


def test_rejects_a_dataset_with_no_bars(tmp_path: Path) -> None:
    bars_path = tmp_path / "bars.parquet"
    bars_to_frame([]).to_parquet(bars_path, index=False)
    with pytest.raises(ValueError, match="no Bars"):
        read_bars(bars_path)


def test_rejects_a_dataset_written_from_another_shape(tmp_path: Path) -> None:
    bars_path = tmp_path / "bars.parquet"
    pd.DataFrame({"symbol": ["AAPL"], "close": [100.0]}).to_parquet(bars_path, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        read_bars(bars_path)
