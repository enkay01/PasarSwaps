"""The Alpaca Source, against a fake transport so no test touches the network."""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import timedelta
from typing import NotRequired, TypedDict

import pytest

from alpaca import (
    DEFAULT_SETTINGS,
    AlpacaBarSource,
    AlpacaSettings,
    AlpacaCredentials,
    HttpResponse,
    JsonTransport,
    JsonValue,
    SourceError,
)
from support import DAY_ZERO

CREDENTIALS = AlpacaCredentials(api_key="key-id", api_secret="secret-key")
NO_PACING = replace(DEFAULT_SETTINGS, request_interval_seconds=0.0)
WINDOW_END = DAY_ZERO + timedelta(days=10)


class BarPayload(TypedDict):
    """One Bar exactly as the Alpaca JSON carries it."""

    t: str
    o: float
    h: float
    l: float
    c: float
    v: int
    n: int
    vw: float


class PagePayload(TypedDict):
    """One page of the Alpaca bars response."""

    bars: dict[str, list[JsonValue]]
    next_page_token: NotRequired[str]


class FakeTransport:
    """Return the canned replies in order and remember every request."""

    def __init__(self, replies: Sequence[HttpResponse]) -> None:
        self._replies = list(replies)
        self.requests: list[tuple[str, dict[str, str], dict[str, str]]] = []

    def get(self, url: str, params: Mapping[str, str], headers: Mapping[str, str]) -> HttpResponse:
        self.requests.append((url, dict(params), dict(headers)))
        if not self._replies:
            raise AssertionError("the Source asked for more replies than the test supplied")
        return self._replies.pop(0)


class RecordingSleep:
    """Stand in for time.sleep so no test waits."""

    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


def bar_body(day: str, close: float) -> BarPayload:
    return {"t": f"{day}T20:00:00Z", "o": close, "h": close, "l": close, "c": close, "v": 10, "n": 1, "vw": close}


def bars_reply(bars: Mapping[str, Sequence[JsonValue]], token: str | None = None) -> HttpResponse:
    page: PagePayload = {"bars": {symbol: list(items) for symbol, items in bars.items()}}
    if token is not None:
        page["next_page_token"] = token
    return HttpResponse(status=200, headers={}, body=page)


def build_source(
    transport: JsonTransport,
    settings: AlpacaSettings = NO_PACING,
    sleep: RecordingSleep | None = None,
) -> AlpacaBarSource:
    return AlpacaBarSource(transport, CREDENTIALS, settings, sleep=sleep or RecordingSleep())


def test_sends_the_credentials_the_feed_and_the_daily_timeframe() -> None:
    transport = FakeTransport([bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]})] * 2)
    build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    headers = transport.requests[0][2]
    params = transport.requests[0][1]
    assert headers["APCA-API-KEY-ID"] == "key-id"
    assert headers["APCA-API-SECRET-KEY"] == "secret-key"
    assert params["timeframe"] == "1Day"
    assert params["feed"] == "iex"
    assert params["symbols"] == "AAPL"


def test_asks_for_the_raw_bars_then_the_adjusted_bars() -> None:
    transport = FakeTransport([bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]})] * 2)
    build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert [request[1]["adjustment"] for request in transport.requests] == ["raw", "all"]


def test_keeps_the_raw_close_beside_the_adjusted_close() -> None:
    transport = FakeTransport(
        [
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 50.0)]}),
        ]
    )
    bars = build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert bars[0].close == 100.0
    assert bars[0].adjusted_close == 50.0


def test_follows_the_page_token_to_the_end_of_the_batch() -> None:
    transport = FakeTransport(
        [
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}, token="next"),
            bars_reply({"AAPL": [bar_body("2024-01-03", 101.0)]}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}, token="next"),
            bars_reply({"AAPL": [bar_body("2024-01-03", 101.0)]}),
        ]
    )
    bars = build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert [bar.date for bar in bars] == [DAY_ZERO, DAY_ZERO + timedelta(days=1)]
    assert "page_token" not in transport.requests[0][1]
    assert transport.requests[1][1]["page_token"] == "next"
    assert "page_token" not in transport.requests[2][1]
    assert transport.requests[3][1]["page_token"] == "next"


def test_splits_the_symbol_list_into_batches() -> None:
    transport = FakeTransport([bars_reply({}) for _ in range(4)])
    settings = replace(NO_PACING, symbols_per_request=2)
    build_source(transport, settings).fetch_daily_bars(["AAA", "BBB", "CCC"], DAY_ZERO, WINDOW_END)
    assert [request[1]["symbols"] for request in transport.requests] == ["AAA,BBB", "AAA,BBB", "CCC", "CCC"]


def test_paces_requests_under_the_plan_limit() -> None:
    sleep = RecordingSleep()
    transport = FakeTransport([bars_reply({}) for _ in range(2)])
    settings = replace(DEFAULT_SETTINGS, symbols_per_request=1)
    build_source(transport, settings, sleep).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert sleep.delays == [DEFAULT_SETTINGS.request_interval_seconds]


def test_retries_a_rate_limited_request() -> None:
    sleep = RecordingSleep()
    transport = FakeTransport(
        [
            HttpResponse(status=429, headers={}, body={"message": "slow down"}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
        ]
    )
    bars = build_source(transport, NO_PACING, sleep).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert len(bars) == 1
    assert sleep.delays == [DEFAULT_SETTINGS.retry_base_seconds]


def test_waits_as_long_as_the_retry_after_header_asks() -> None:
    sleep = RecordingSleep()
    transport = FakeTransport(
        [
            HttpResponse(status=429, headers={"retry-after": "7"}, body={"message": "slow down"}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
        ]
    )
    build_source(transport, NO_PACING, sleep).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert sleep.delays == [7.0]


def test_gives_up_after_the_last_attempt() -> None:
    sleep = RecordingSleep()
    settings = replace(NO_PACING, max_attempts=2)
    transport = FakeTransport([HttpResponse(status=429, headers={}, body={"message": "slow down"})] * 2)
    with pytest.raises(SourceError, match="HTTP 429"):
        build_source(transport, settings, sleep).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert len(transport.requests) == 2
    assert sleep.delays == [DEFAULT_SETTINGS.retry_base_seconds]


def test_does_not_retry_a_forbidden_request() -> None:
    sleep = RecordingSleep()
    transport = FakeTransport([HttpResponse(status=403, headers={}, body={"message": "forbidden"})])
    with pytest.raises(SourceError, match="HTTP 403"):
        build_source(transport, NO_PACING, sleep).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert len(transport.requests) == 1
    assert sleep.delays == []


def test_raises_when_the_raw_and_adjusted_bars_do_not_line_up() -> None:
    transport = FakeTransport(
        [
            bars_reply(
                {
                    "AAPL": [
                        bar_body("2024-01-02", 100.0),
                        bar_body("2024-01-03", 101.0),
                    ]
                }
            ),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}),
        ]
    )
    with pytest.raises(SourceError, match="line up"):
        build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_rejects_a_body_that_is_not_a_page() -> None:
    transport = FakeTransport([HttpResponse(status=200, headers={}, body=["not", "an", "object"])])
    with pytest.raises(SourceError, match="not a JSON object"):
        build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_rejects_a_page_without_a_bars_field() -> None:
    transport = FakeTransport([HttpResponse(status=200, headers={}, body={"message": "nothing here"})])
    with pytest.raises(SourceError, match="without a bars field"):
        build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_treats_an_empty_page_token_as_the_end_of_the_batch() -> None:
    transport = FakeTransport(
        [
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}, token=""),
            bars_reply({"AAPL": [bar_body("2024-01-02", 100.0)]}, token=""),
        ]
    )
    bars = build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert len(transport.requests) == 2
    assert len(bars) == 1


def test_rejects_a_bar_without_a_close() -> None:
    incomplete: JsonValue = {"t": "2024-01-02T20:00:00Z", "o": 1.0, "h": 1.0, "l": 1.0, "v": 1}
    transport = FakeTransport([bars_reply({"AAPL": [incomplete]})])
    with pytest.raises(SourceError, match="without c"):
        build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_rejects_a_close_that_is_not_a_number() -> None:
    stringly: JsonValue = {**bar_body("2024-01-02", 100.0), "c": "high"}
    transport = FakeTransport([bars_reply({"AAPL": [stringly]})])
    with pytest.raises(SourceError, match="not a number"):
        build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_rejects_a_symbol_batch_size_below_one() -> None:
    settings = replace(NO_PACING, symbols_per_request=0)
    with pytest.raises(ValueError, match="at least 1"):
        build_source(FakeTransport([]), settings).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)


def test_asks_for_nothing_when_the_symbol_list_is_empty() -> None:
    transport = FakeTransport([])
    assert build_source(transport).fetch_daily_bars([], DAY_ZERO, WINDOW_END) == []
    assert transport.requests == []


def test_never_asks_beyond_the_requested_window() -> None:
    transport = FakeTransport([bars_reply({}), bars_reply({})])
    build_source(transport).fetch_daily_bars(["AAPL"], DAY_ZERO, WINDOW_END)
    assert [request[1]["start"] for request in transport.requests] == [DAY_ZERO.isoformat()] * 2
    assert [request[1]["end"] for request in transport.requests] == [WINDOW_END.isoformat()] * 2


def test_bars_come_back_in_symbol_and_date_order() -> None:
    page = {
        "MSFT": [bar_body("2024-01-02", 200.0)],
        "AAPL": [bar_body("2024-01-03", 101.0), bar_body("2024-01-02", 100.0)],
    }
    transport = FakeTransport([bars_reply(page), bars_reply(page)])
    bars = build_source(transport).fetch_daily_bars(["AAPL", "MSFT"], DAY_ZERO, WINDOW_END)
    assert [(bar.symbol, bar.date) for bar in bars] == [
        ("AAPL", DAY_ZERO),
        ("AAPL", DAY_ZERO + timedelta(days=1)),
        ("MSFT", DAY_ZERO),
    ]
