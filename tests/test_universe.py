"""The Universe reader."""

from pathlib import Path

import pytest

from universe import read_universe


def write_universe(path: Path, rows: str) -> Path:
    path.write_text(rows, encoding="utf-8")
    return path


def test_reads_the_symbols_in_file_order(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", "Symbol,Security\nMSFT,Microsoft\nAAPL,Apple\n")
    assert read_universe(universe) == ["MSFT", "AAPL"]


def test_strips_whitespace_and_drops_duplicates(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", "Symbol\n AAPL \nAAPL\nMSFT\n")
    assert read_universe(universe) == ["AAPL", "MSFT"]


def test_skips_rows_without_a_symbol(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", "Symbol,Security\nAAPL,Apple\n,Unknown\n")
    assert read_universe(universe) == ["AAPL"]


def test_rejects_a_file_without_the_symbol_column(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", "Ticker\nAAPL\n")
    with pytest.raises(ValueError, match="Symbol"):
        read_universe(universe)


def test_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_universe(tmp_path / "absent.csv")


def test_rejects_a_universe_with_no_symbols(tmp_path: Path) -> None:
    universe = write_universe(tmp_path / "universe.csv", "Symbol,Security\n")
    with pytest.raises(ValueError, match="no symbols"):
        read_universe(universe)
