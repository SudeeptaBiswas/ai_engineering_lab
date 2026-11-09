"""Tests for assistant/ollama_client.py: 5 with fakes + 1 real (Ollama).
Fill the stubs in assistant/ollama_client.py until all pass.

  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_2_client.py -v
Ollama off? Add -m "not ollama".
"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

import httpx
import pytest

from assistant.memory import Message
from assistant.ollama_client import MAX_ANSWER_TOKENS, MODEL, NUM_CTX, chat_body, chunk_text, stream_chat

HI: list[Message] = [{"role": "user", "content": "Say hi."}]
# Real lines from qwen3:1.7b (lesson 2.3). The last one has content "".
LINES = [
    '{"message":{"role":"assistant","content":"R"},"done":false}',
    '{"message":{"role":"assistant","content":"AG"},"done":false}',
    "",
    '{"message":{"role":"assistant","content":" helps"},"done":false}',
    '{"message":{"role":"assistant","content":""},"done":true,"done_reason":"stop"}',
]

FakeStream = Callable[..., Any]  # what make_fake_stream returns


# ---------- Fake httpx.stream (done for you) ----------
# httpx.stream is used as `with httpx.stream(...) as response:`. A fake for
# it must work with `with` too. @contextmanager does that: code before
# `yield` = start of the with-block, the yielded value = `response`.
# Java: an AutoCloseable used in try-with-resources.
def make_fake_stream(status: int, lines: list[str], sent_bodies: list[Any]) -> FakeStream:
    """Build a stand-in for httpx.stream that never touches the network.

    Args:
        status: HTTP status to answer with, e.g. 200 or 404.
        lines: the NDJSON lines to send back, e.g. LINES.
        sent_bodies: an empty list; each call's json= body is added to it.
    Returns:
        A function with the same use as httpx.stream.
    """
    @contextmanager
    def fake_stream(method: str, url: str, **options: Any) -> Generator[httpx.Response]:
        """Saves the json= body, then hands out a ready-made response.

        Args:
            method: "POST".
            url: e.g. "http://127.0.0.1:11434/api/chat".
            options: json=..., timeout=... (any keyword arguments).
        Returns:
            (via yield) an httpx.Response holding `lines`.
        """
        sent_bodies.append(options.get("json"))
        content = "\n".join(lines).encode()  # str -> bytes, like the network gives
        yield httpx.Response(status, content=content, request=httpx.Request(method, url))

    return fake_stream


# ---------- No HTTP ----------
def test_chat_body() -> None:
    """Streaming on, thinking off, context size and answer length set."""
    assert chat_body(HI) == {
        "model": MODEL,
        "messages": HI,
        "stream": True,
        "think": False,
        "options": {"num_ctx": NUM_CTX, "num_predict": MAX_ANSWER_TOKENS},
    }


@pytest.mark.parametrize(("line", "expected"), [(LINES[1], "AG"), (LINES[4], ""), ("", ""), ("  ", "")])
def test_chunk_text(line: str, expected: str) -> None:
    """One stream line -> its text; blank lines give "" (no crash).

    Args:
        line: one NDJSON line.
        expected: the text in it.
    """
    assert chunk_text(line) == expected


# ---------- Fake HTTP ----------
def test_stream_chat_yields_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-empty chunks, in order. The final "" is skipped (the 2.3 bug).

    Args:
        monkeypatch: built-in pytest fixture.
    """
    monkeypatch.setattr(httpx, "stream", make_fake_stream(200, LINES, []))
    chunks: list[str] = []
    for chunk in stream_chat(HI):
        chunks.append(chunk)
    assert chunks == ["R", "AG", " helps"]


def test_stream_chat_sends_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exactly one call, and its body is chat_body(messages).

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent_bodies: list[Any] = []
    monkeypatch.setattr(httpx, "stream", make_fake_stream(200, LINES, sent_bodies))
    for _ in stream_chat(HI):  # a generator does nothing until looped over
        pass
    assert sent_bodies == [chat_body(HI)]


def test_stream_chat_bad_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """404 (model not pulled) must raise HTTPStatusError, not yield nothing.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    error_line = '{"error":"model \\"qwen3:1.7b\\" not found"}'
    monkeypatch.setattr(httpx, "stream", make_fake_stream(404, [error_line], []))
    with pytest.raises(httpx.HTTPStatusError):
        for _ in stream_chat(HI):
            pass


# ---------- Real Ollama ----------
@pytest.mark.ollama
def test_stream_chat_real() -> None:
    """The real model streams more than one non-empty chunk for "Say hi."."""
    chunks: list[str] = []
    for chunk in stream_chat(HI):
        chunks.append(chunk)
    assert len(chunks) > 1
    assert "" not in chunks
