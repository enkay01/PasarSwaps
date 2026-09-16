"""The Bar record and the Dataset frame."""

from datetime import timedelta

import pandas as pd

from bars import COLUMNS, bars_to_frame
from support import DAY_ZERO, make_bar


def test_holds_the_stored_columns_in_order() -> None:
    frame = bars_to_frame([make_bar()])
    assert list(frame.columns) == list(COLUMNS)


def test_holds_one_row_per_bar() -> None:
    frame = bars_to_frame([make_bar(symbol="AAPL"), make_bar(symbol="MSFT", close=200.0)])
    assert frame["symbol"].tolist() == ["AAPL", "MSFT"]
    assert frame["close"].tolist() == [100.0, 200.0]


def test_keeps_the_raw_close_beside_the_adjusted_close() -> None:
    frame = bars_to_frame([make_bar(close=100.0, adjusted_close=50.0)])
    assert frame["close"].tolist() == [100.0]
    assert frame["adjusted_close"].tolist() == [50.0]


def test_stores_the_date_as_a_timestamp_and_the_volume_as_an_integer() -> None:
    frame = bars_to_frame([make_bar(day=DAY_ZERO + timedelta(days=1))])
    assert frame["date"].iloc[0] == pd.Timestamp(DAY_ZERO + timedelta(days=1))
    assert frame["volume"].iloc[0] == 1_000
    assert frame["volume"].dtype == "int64"


def test_keeps_the_columns_when_there_are_no_bars() -> None:
    frame = bars_to_frame([])
    assert list(frame.columns) == list(COLUMNS)
    assert frame.empty
