"""Where the lab keeps its files."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent
DATA_DIRECTORY = REPOSITORY_ROOT / "data"
UNIVERSE_CSV = DATA_DIRECTORY / "sp500_constituents.csv"
BARS_PARQUET = DATA_DIRECTORY / "sp500_daily_bars.parquet"
ENV_FILE = REPOSITORY_ROOT / ".env.local"
