"""The HTTP transport, against a real socket on localhost."""

from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from alpaca import RequestsTransport

BAR_PAGE = (
    b'{"bars": {"AAPL": [{"t": "2024-01-02T20:00:00Z", "o": 1.0, "h": 2.0, '
    b'"l": 1.0, "c": 1.5, "v": 5, "n": 1, "vw": 1.4}]}, "next_page_token": null}'
)


class BarHandler(BaseHTTPRequestHandler):
    """Answer every GET with the same Bars page."""

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(BAR_PAGE)))
        self.end_headers()
        self.wfile.write(BAR_PAGE)

    def log_message(self, format: str, *args: object) -> None:
        """Keep the test output clean."""


@contextmanager
def local_server(handler: type[BaseHTTPRequestHandler]) -> Iterator[str]:
    """Serve on a free port and give back the base URL until the block ends."""
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_returns_the_status_and_a_lower_cased_header_map() -> None:
    with local_server(BarHandler) as base_url:
        response = RequestsTransport(timeout_seconds=5.0).get(f"{base_url}/v2/stocks/bars", {}, {})
    assert response.status == 200
    assert response.headers["content-type"] == "application/json"


def test_parses_a_json_body_into_json_values() -> None:
    with local_server(BarHandler) as base_url:
        response = RequestsTransport(timeout_seconds=5.0).get(base_url, {}, {})
    assert isinstance(response.body, dict)
    assert response.body["next_page_token"] is None
    assert response.body["bars"]["AAPL"][0]["c"] == 1.5
