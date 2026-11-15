"""A fake httpx.stream for the client tests (no network). Not a test file.

httpx.stream is used as `with httpx.stream(...) as response:`, so the fake
must work with `with` too. @contextmanager does that: the code before
`yield` = the start of the with-block, the yielded value = `response`.
Used by exercises_2_6_2_client.py.
"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

import httpx

from lab_tools.log import debug, log

FakeStream = Callable[..., Any]  # the type of what make_fake_stream returns


@debug
def make_fake_stream(status_code: int, stream_lines: list[str], sent_bodies: list[Any]) -> FakeStream:
    """Build a stand-in for httpx.stream that answers with ready-made lines.

    Args:
        status_code: the HTTP status to answer with, e.g. 200 or 404.
        stream_lines: the NDJSON lines to send back, one per reply line.
        sent_bodies: an empty list; each call's json= body is added to it,
            so a test can check what was sent.
    Returns:
        A function used like httpx.stream.
    """
    log.debug("start: status %d, %d lines", status_code, len(stream_lines))

    @contextmanager
    @debug
    def fake_stream(method: str, url: str, **options: Any) -> Generator[httpx.Response]:
        """Save the json= body, then hand out a response holding stream_lines.

        Args:
            method: "POST".
            url: e.g. "http://127.0.0.1:11434/api/chat".
            options: json=..., timeout=... (any keyword arguments).
        Returns:
            (via yield) an httpx.Response.
        """
        sent_bodies.append(options.get("json"))
        response_bytes = "\n".join(stream_lines).encode()  # text -> bytes, like the network gives
        fake_request = httpx.Request(method, url)  # raise_for_status needs to know the request
        fake_response = httpx.Response(status_code, content=response_bytes, request=fake_request)
        log.debug("fake %s %s -> status %d", method, url, status_code)
        yield fake_response

    return fake_stream
