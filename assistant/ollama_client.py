"""Talks to Ollama: one streaming POST /api/chat (lessons 2.3 and 3.3).

The reply comes back line by line (NDJSON). Each line holds a piece of the
answer text, or the tools the model wants us to run (v2), or nothing.

Tests: 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_2_client.py (text)
       03_prompting_tools/3_5_assistant_v2/test_3_5_3_client.py (tool calls)
"""

import json  # json.loads: JSON text -> dict
from collections.abc import Iterator  # what a generator function returns
from dataclasses import dataclass, field
from typing import Any  # "any type": JSON values can be anything

import httpx

from assistant.memory import Message
from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows (1.7)
MODEL = "qwen3:1.7b"  # think=False works here; 4b leaks thinking (2.3)
NUM_CTX = 4096  # context size in tokens; the default `ollama ps` showed. Sent explicitly
MAX_ANSWER_TOKENS = 300  # num_predict: hard limit on the answer length (2.3)
TEMPERATURE = 0  # steady tool choices; 3.3 and 3.4 were measured at 0
SEED = 42  # same question -> same answer (2.4)
REQUEST_TIMEOUT_SECONDS = 120.0


@dataclass
class ToolCall:
    """One tool the model asks us to run, e.g. order_status(order_id="A-1001")."""

    tool_name: str  # e.g. "order_status"
    tool_arguments: dict[str, Any]  # e.g. {"order_id": "A-1001"}; the model picks them, never trust them


@dataclass
class StreamPiece:
    """What one stream line carries: some answer text, tool calls, or both empty."""

    text: str  # e.g. "AG"; "" when the line has no text
    tool_calls: list[ToolCall] = field(default_factory=list[ToolCall])  # a new empty list for each piece


def build_request_body(chat_messages: list[Message], tool_specs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the JSON body for one streaming POST /api/chat.

    Args:
        chat_messages: the messages for this call, e.g. memory.messages_to_send().
        tool_specs: what the model reads about each tool (tool_runner.build_tool_specs()),
            or [] for no tools.
    Returns:
        e.g. {"model": MODEL, "messages": [...], "stream": True, "think": False,
              "tools": [...], "options": {...}}.
    """
    options = {"num_ctx": NUM_CTX, "num_predict": MAX_ANSWER_TOKENS, "temperature": TEMPERATURE, "seed": SEED}
    request_body: dict[str, Any] = {
        "model": MODEL,
        "messages": chat_messages,
        "stream": True,  # the answer comes line by line
        "think": False,  # no hidden thinking text
        "tools": tool_specs,
        "options": options,
    }
    return request_body


def parse_stream_line(stream_line: str) -> StreamPiece:
    """Read one stream line: the answer text in it and any tool calls.

    How:
        1. A blank line -> an empty piece (no crash).
        2. Parse the JSON; take "message" (missing -> {}).
        3. Text = message["content"]; each entry of message["tool_calls"]
           becomes a ToolCall.
    Args:
        stream_line: e.g. '{"message":{"role":"assistant","content":"AG"},"done":false}'.
    Returns:
        e.g. StreamPiece(text="AG", tool_calls=[]).
    """
    if not stream_line.strip():  # blank line: nothing to parse
        empty_piece = StreamPiece(text="")
        return empty_piece
    line_json: dict[str, Any] = json.loads(stream_line)
    message_part: dict[str, Any] = line_json.get("message", {})  # no "message" key -> {}
    answer_text = str(message_part.get("content", ""))
    raw_tool_calls: list[dict[str, Any]] = message_part.get("tool_calls") or []  # None or missing -> []
    tool_calls: list[ToolCall] = []
    for raw_tool_call in raw_tool_calls:
        function_part: dict[str, Any] = raw_tool_call["function"]  # {"name": ..., "arguments": {...}}
        tool_call = ToolCall(tool_name=function_part["name"], tool_arguments=function_part.get("arguments", {}))
        tool_calls.append(tool_call)
    stream_piece = StreamPiece(text=answer_text, tool_calls=tool_calls)
    return stream_piece


@debug
def stream_reply(chat_messages: list[Message], tool_specs: list[dict[str, Any]]) -> Iterator[StreamPiece]:
    """Send the messages to the model and hand back its reply piece by piece (a generator).

    How:
        1. POST the request body with streaming on.
        2. Stop with an error on a bad status (e.g. 404 = model not pulled).
        3. For each stream line: parse it; hand it out only if it has
           text or tool calls (the last "done" line has neither).
    Args:
        chat_messages: the messages for this call.
        tool_specs: the tools the model may ask for, or [].
    Returns:
        A generator of StreamPiece, e.g. text "R", "AG", " helps".
    Raises:
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
        httpx.ConnectError: Ollama is not running.
    """
    chat_url = f"{OLLAMA_URL}/api/chat"
    request_body = build_request_body(chat_messages, tool_specs)
    last_message = chat_messages[-1]
    log.debug("start: %d messages, %d tools, last=%s", len(chat_messages), len(tool_specs),
              cut_text(last_message["content"]))
    # `with` closes the connection at the end, also on an error
    with httpx.stream("POST", chat_url, json=request_body, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        response.raise_for_status()  # 404 / 500 -> HTTPStatusError
        for stream_line in response.iter_lines():
            stream_piece = parse_stream_line(stream_line)
            has_content = stream_piece.text != "" or len(stream_piece.tool_calls) > 0
            if has_content:
                yield stream_piece
    log.debug("result: stream finished")
