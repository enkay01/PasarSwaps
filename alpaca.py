"""The Alpaca Source: one symbol list per request, paged, paced and retried.

The previous lab fetched one symbol per call and died partway through a run.
This Source sends a list of symbols in each request, follows every page, and
paces its requests under the Basic plan's 200 calls a minute.
"""

from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from datetime import date, datetime
import json
import time
from typing import Protocol, Union

import requests

from bars import Bar

DATA_URL = "https://data.alpaca.markets"
BARS_PATH = "/v2/stocks/bars"
RAW_ADJUSTMENT = "raw"
ALL_ADJUSTMENT = "all"
TIMEFRAME = "1Day"
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})

# The shape of any JSON document, so the untrusted reply has a named type.
JsonValue = Union[str, int, float, bool, None, list["JsonValue"], dict[str, "JsonValue"]]


class SourceError(RuntimeError):
    """The Source returned something the download cannot use."""


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """One reply from the transport, with the status and headers a retry needs.

    Header names are lower case, so a lookup does not depend on how the server cased them.
    """

    status: int
    headers: Mapping[str, str]
    body: JsonValue


class JsonTransport(Protocol):
    """One HTTP GET. Pacing and retries belong to the caller."""

    def get(self, url: str, params: Mapping[str, str], headers: Mapping[str, str]) -> HttpResponse:
        """Send one GET and return the reply without raising on an error status."""
        ...


class RequestsTransport:
    """The real transport. One GET per call, with a timeout and no retry."""

    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def get(self, url: str, params: Mapping[str, str], headers: Mapping[str, str]) -> HttpResponse:
        response = requests.get(
            url,
            params=dict(params),
            headers=dict(headers),
            timeout=self._timeout_seconds,
        )
        return HttpResponse(
            status=response.status_code,
            headers={name.lower(): value for name, value in response.headers.items()},
            body=_parsed_body(response.text),
        )


@dataclass(frozen=True, slots=True)
class AlpacaSettings:
    """The knobs that keep one run inside the Alpaca Basic plan."""

    feed: str
    page_limit: int
    symbols_per_request: int
    request_interval_seconds: float
    max_attempts: int
    retry_base_seconds: float
    retry_cap_seconds: float


DEFAULT_SETTINGS = AlpacaSettings(
    feed="iex",
    page_limit=10_000,
    symbols_per_request=100,
    request_interval_seconds=0.35,
    max_attempts=5,
    retry_base_seconds=2.0,
    retry_cap_seconds=60.0,
)


@dataclass(frozen=True, slots=True)
class AlpacaCredentials:
    """The key and secret the Alpaca dashboard shows."""

    api_key: str
    api_secret: str


@dataclass(frozen=True, slots=True)
class RawBar:
    """One Bar as the Source returned it, before the two adjustments are merged."""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True, slots=True)
class BarPage:
    """One page of Bars and the token that reaches the next page."""

    bars: Mapping[tuple[str, date], RawBar]
    next_token: str | None


@dataclass(frozen=True, slots=True)
class PageQuery:
    """Everything one Bars request carries besides the credentials."""

    symbols: Sequence[str]
    start: date
    end: date
    adjustment: str
    token: str | None


class AlpacaBarSource:
    """Fetch daily Bars from Alpaca for a symbol list, raw and adjusted."""

    def __init__(
        self,
        transport: JsonTransport,
        credentials: AlpacaCredentials,
        settings: AlpacaSettings,
        *,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._transport = transport
        self._credentials = credentials
        self._settings = settings
        self._sleep = sleep
        self._requests_made = 0

    def fetch_daily_bars(self, symbols: Sequence[str], start: date, end: date) -> list[Bar]:
        """Fetch every Bar for every symbol, in one pass for each adjustment."""
        bars: list[Bar] = []
        for batch in _batched(symbols, self._settings.symbols_per_request):
            raw = self._fetch(batch, start, end, RAW_ADJUSTMENT)
            adjusted = self._fetch(batch, start, end, ALL_ADJUSTMENT)
            bars.extend(_merge(raw, adjusted))
        return bars

    def _fetch(self, symbols: Sequence[str], start: date, end: date, adjustment: str) -> dict[tuple[str, date], RawBar]:
        collected: dict[tuple[str, date], RawBar] = {}
        token: str | None = None
        while True:
            page = self._get_page(PageQuery(symbols=symbols, start=start, end=end, adjustment=adjustment, token=token))
            collected.update(page.bars)
            token = page.next_token
            if token is None:
                return collected

    def _get_page(self, query: PageQuery) -> BarPage:
        params = self._params(query)
        for attempt in range(1, self._settings.max_attempts + 1):
            self._pace()
            response = self._transport.get(f"{DATA_URL}{BARS_PATH}", params, self._headers())
            if response.status == 200:
                return _parse_page(response.body)
            if response.status not in RETRYABLE_STATUSES or attempt == self._settings.max_attempts:
                raise SourceError(f"Alpaca returned HTTP {response.status}: {_snippet(response.body)}")
            self._sleep(self._retry_delay(attempt, response.headers))
        raise SourceError("Alpaca request retries ran out")

    def _pace(self) -> None:
        if self._requests_made and self._settings.request_interval_seconds > 0:
            self._sleep(self._settings.request_interval_seconds)
        self._requests_made += 1

    def _retry_delay(self, attempt: int, headers: Mapping[str, str]) -> float:
        backoff = min(
            self._settings.retry_base_seconds * 2 ** (attempt - 1),
            self._settings.retry_cap_seconds,
        )
        return max(backoff, _header_seconds(headers.get("retry-after")))

    def _params(self, query: PageQuery) -> dict[str, str]:
        params = {
            "symbols": ",".join(query.symbols),
            "timeframe": TIMEFRAME,
            "start": query.start.isoformat(),
            "end": query.end.isoformat(),
            "limit": str(self._settings.page_limit),
            "adjustment": query.adjustment,
            "feed": self._settings.feed,
            "sort": "asc",
        }
        if query.token is not None:
            params["page_token"] = query.token
        return params

    def _headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self._credentials.api_key,
            "APCA-API-SECRET-KEY": self._credentials.api_secret,
            "Accept": "application/json",
        }


def _batched(symbols: Sequence[str], size: int) -> Iterator[Sequence[str]]:
    if size < 1:
        raise ValueError("symbols_per_request must be at least 1")
    for start in range(0, len(symbols), size):
        yield symbols[start : start + size]


def _merge(
    raw: Mapping[tuple[str, date], RawBar],
    adjusted: Mapping[tuple[str, date], RawBar],
) -> list[Bar]:
    missing_adjusted = set(raw) - set(adjusted)
    missing_raw = set(adjusted) - set(raw)
    if missing_adjusted or missing_raw:
        raise SourceError(
            "Alpaca returned raw and adjusted Bars that do not line up: "
            f"{len(missing_adjusted)} without an adjusted close, "
            f"{len(missing_raw)} without a raw Bar, first {_first_key(missing_adjusted or missing_raw)}"
        )
    return [
        Bar(
            symbol=key[0],
            date=key[1],
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            adjusted_close=adjusted[key].close,
        )
        for key, bar in sorted(raw.items())
    ]


def _first_key(keys: set[tuple[str, date]]) -> str:
    symbol, day = min(keys)
    return f"{symbol} {day}"


def _parsed_body(text: str) -> JsonValue:
    """The reply as JSON when the server sent JSON, and as text otherwise."""
    with suppress(ValueError):
        return json.loads(text)
    return text


def _parse_page(body: JsonValue) -> BarPage:
    if not isinstance(body, dict):
        raise SourceError("Alpaca returned a body that is not a JSON object")
    if "bars" not in body:
        raise SourceError("Alpaca returned a page without a bars field")
    raw_bars = body["bars"]
    if not isinstance(raw_bars, dict):
        raise SourceError("Alpaca returned a bars field that is not an object")
    bars: dict[tuple[str, date], RawBar] = {}
    for symbol, items in raw_bars.items():
        if not isinstance(items, list):
            raise SourceError(f"Alpaca returned no list of Bars for {symbol}")
        for item in items:
            bar = _parse_bar(str(symbol), item)
            bars[(bar.symbol, bar.date)] = bar
    token = body.get("next_page_token")
    if token is not None and not isinstance(token, str):
        raise SourceError("Alpaca returned a page token that is not a string")
    return BarPage(bars=bars, next_token=token or None)


def _parse_bar(symbol: str, item: JsonValue) -> RawBar:
    if not isinstance(item, dict):
        raise SourceError(f"Alpaca returned a Bar for {symbol} that is not an object")
    try:
        timestamp = item["t"]
        open_price = item["o"]
        high_price = item["h"]
        low_price = item["l"]
        close_price = item["c"]
        volume = item["v"]
    except KeyError as error:
        raise SourceError(f"Alpaca returned a Bar for {symbol} without {error.args[0]}") from error
    if not isinstance(timestamp, str):
        raise SourceError(f"Alpaca returned a Bar for {symbol} with an unreadable timestamp")
    return RawBar(
        symbol=symbol,
        date=_bar_date(timestamp, symbol),
        open=_number(open_price, symbol, "o"),
        high=_number(high_price, symbol, "h"),
        low=_number(low_price, symbol, "l"),
        close=_number(close_price, symbol, "c"),
        volume=int(_number(volume, symbol, "v")),
    )


def _number(value: JsonValue, symbol: str, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SourceError(f"Alpaca returned a {field} for {symbol} that is not a number")
    return float(value)


def _bar_date(timestamp: str, symbol: str) -> date:
    try:
        moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as error:
        raise SourceError(f"Alpaca returned an unreadable timestamp for {symbol}: {timestamp}") from error
    return moment.date()


def _header_seconds(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return max(0.0, float(value))
    except ValueError:
        return 0.0


def _snippet(body: JsonValue) -> str:
    text = body if isinstance(body, str) else repr(body)
    return text[:200]
