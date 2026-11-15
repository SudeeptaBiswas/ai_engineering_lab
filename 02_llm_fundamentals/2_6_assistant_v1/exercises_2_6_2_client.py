"""Tests for assistant/ollama_client.py, text part: 5 with a fake HTTP stream + 1 real.

Tool calls in the stream: 03_prompting_tools/3_5_assistant_v2/test_3_5_3_client.py.
  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_2_client.py -v
Ollama off? Add -m "not ollama".
"""

from typing import Any

import httpx
import pytest

from assistant.memory import Message
from assistant.ollama_client import (CHAT_MODEL, MAX_ANSWER_TOKENS, NUM_CTX, SEED, TEMPERATURE, StreamPiece,
                                     build_request_body, parse_stream_line, stream_reply)
from fakes_2_6_2_stream import make_fake_stream
from lab_tools.log import debug, log

SAY_HI_MESSAGES: list[Message] = [{"role": "user", "content": "Say hi."}]
NO_TOOLS: list[dict[str, Any]] = []
# Real lines from qwen3:1.7b (lesson 2.3). The last one has content "".
TEXT_LINE = '{"message":{"role":"assistant","content":"AG"},"done":false}'
DONE_LINE = '{"message":{"role":"assistant","content":""},"done":true,"done_reason":"stop"}'
REAL_STREAM_LINES = [
    '{"message":{"role":"assistant","content":"R"},"done":false}',
    TEXT_LINE,
    "",
    '{"message":{"role":"assistant","content":" helps"},"done":false}',
    DONE_LINE,
]


@debug
def collect_texts(stream_pieces: list[StreamPiece]) -> list[str]:
    """Take just the text of each piece.

    Args:
        stream_pieces: e.g. what stream_reply handed out.
    Returns:
        e.g. ["R", "AG", " helps"].
    """
    texts: list[str] = []
    for stream_piece in stream_pieces:
        texts.append(stream_piece.text)
    log.debug("result: %s", texts)
    return texts


@debug
def test_request_body_has_streaming_on_and_thinking_off() -> None:
    """Every setting is in the body: streaming, no thinking, sizes, steady sampling.

    Why: a missing num_ctx means Ollama's default, and a silent cut (2.6 part 1).
    """
    expected_options = {"num_ctx": NUM_CTX, "num_predict": MAX_ANSWER_TOKENS, "temperature": TEMPERATURE, "seed": SEED}
    expected_body = {"model": CHAT_MODEL, "messages": SAY_HI_MESSAGES, "stream": True, "think": False,
                     "tools": NO_TOOLS, "options": expected_options}
    request_body = build_request_body(SAY_HI_MESSAGES, NO_TOOLS)
    log.debug("expected=%s got=%s", expected_body, request_body)
    assert request_body == expected_body


@pytest.mark.parametrize(("stream_line", "expected_text"), [
    (TEXT_LINE, "AG"),  # a normal text line
    (DONE_LINE, ""),    # the last "done" line has no text
    ("", ""),           # a blank line must not crash
    ("  ", ""),         # spaces only, same
])
@debug
def test_parse_stream_line_gets_the_text(stream_line: str, expected_text: str) -> None:
    """One stream line -> its text, no tool calls: the answer is glued from these pieces.

    Args:
        stream_line: one NDJSON line.
        expected_text: the text in it.
    """
    stream_piece = parse_stream_line(stream_line)
    log.debug("expected=%r got=%r", expected_text, stream_piece.text)
    assert stream_piece.text == expected_text
    assert stream_piece.tool_calls == []


@debug
def test_stream_reply_skips_empty_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only pieces with text come out, in order: the final "" is skipped (the 2.3 bug).

    Args:
        monkeypatch: pytest's tool to swap httpx.stream for a fake.
    """
    monkeypatch.setattr(httpx, "stream", make_fake_stream(200, REAL_STREAM_LINES, []))
    stream_pieces = list(stream_reply(SAY_HI_MESSAGES, NO_TOOLS))  # list(...) runs the generator to the end
    texts = collect_texts(stream_pieces)
    expected_texts = ["R", "AG", " helps"]
    log.debug("expected=%s got=%s", expected_texts, texts)
    assert texts == expected_texts


@debug
def test_stream_reply_sends_one_request_with_the_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exactly one HTTP call per reply, with build_request_body's body: no extra calls, no lost settings.

    Args:
        monkeypatch: pytest's tool to swap httpx.stream for a fake.
    """
    sent_bodies: list[Any] = []
    monkeypatch.setattr(httpx, "stream", make_fake_stream(200, REAL_STREAM_LINES, sent_bodies))
    list(stream_reply(SAY_HI_MESSAGES, NO_TOOLS))  # a generator does nothing until it is read
    expected_bodies = [build_request_body(SAY_HI_MESSAGES, NO_TOOLS)]
    log.debug("expected=%d bodies got=%d", len(expected_bodies), len(sent_bodies))
    assert sent_bodies == expected_bodies


@debug
def test_stream_reply_raises_on_bad_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """404 (model not pulled) raises HTTPStatusError: an empty answer would hide the real problem.

    Args:
        monkeypatch: pytest's tool to swap httpx.stream for a fake.
    """
    error_line = '{"error":"model \\"qwen3:1.7b\\" not found"}'
    monkeypatch.setattr(httpx, "stream", make_fake_stream(404, [error_line], []))
    log.debug("expected=HTTPStatusError for status 404")
    with pytest.raises(httpx.HTTPStatusError):
        list(stream_reply(SAY_HI_MESSAGES, NO_TOOLS))


@pytest.mark.ollama
@debug
def test_stream_reply_real_model_streams_in_pieces() -> None:
    """The real model answers in more than one non-empty piece: proof that Ollama really streams."""
    stream_pieces = list(stream_reply(SAY_HI_MESSAGES, NO_TOOLS))
    texts = collect_texts(stream_pieces)
    log.debug("expected=more than 1 piece got=%d: %s", len(texts), texts)
    assert len(texts) > 1
    assert "" not in texts
