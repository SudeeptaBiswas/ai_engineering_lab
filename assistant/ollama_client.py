"""Talks to Ollama: POST /api/chat with streaming (lesson 2.3).

Spec = 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_2_client.py
"""

import json  # json.loads for stream lines
from collections.abc import Iterator  # what a generator returns (2.6 part 2)
from typing import Any  # "any type". Java: Object

import httpx

from assistant.memory import Message

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows (1.7)
MODEL = "qwen3:1.7b"  # think=False works here; 4b leaks thinking (2.3)
NUM_CTX = 4096  # context size; what `ollama ps` showed as default. Sent explicitly
MAX_ANSWER_TOKENS = 300  # num_predict: answer length limit (2.3)


def chat_body(messages: list[Message]) -> dict[str, Any]:
    """The JSON body for a streaming POST /api/chat.

    Args:
        messages: e.g. memory.messages().
    Returns:
        {"model": MODEL, "messages": messages, "stream": True, "think": False,
         "options": {"num_ctx": NUM_CTX, "num_predict": MAX_ANSWER_TOKENS}}
    """
    options = {"num_ctx": NUM_CTX, "num_predict": MAX_ANSWER_TOKENS}
    body: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "stream": True,  # answer comes line by line
        "think": False,  # no hidden thinking text
        "options": options,
    }
    return body


def chunk_text(line: str) -> str:
    """The answer text in one stream line.

    Args:
        line: e.g. '{"message":{"role":"assistant","content":"AG"},"done":false}'.
    Returns:
        e.g. "AG". A blank line (or only spaces) gives "", no crash.
    """
    if not line.strip():  # blank line: nothing to parse
        return ""
    data: dict[str, Any] = json.loads(line)  # JSON text -> dict
    message: dict[str, Any] = data.get("message", {})  # no "message" key -> {}
    return str(message.get("content", ""))


def stream_chat(messages: list[Message]) -> Iterator[str]:
    """Send messages, then YIELD the answer piece by piece (a generator).

    Steps: `with httpx.stream("POST", url, json=chat_body(messages),
    timeout=120.0) as response:` -> response.raise_for_status() ->
    for each line in response.iter_lines(): chunk_text(line), yield it if
    not empty (the 2.3 bug: the last line's "" is not a chunk).
    Args:
        messages: e.g. memory.messages().
    Returns:
        A generator of text chunks, e.g. "R", "AG", " helps".
    Raises:
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
        httpx.ConnectError: Ollama not running.
    """
    url = f"{OLLAMA_URL}/api/chat"
    # `with` closes the connection at the end. Java: try-with-resources
    with httpx.stream("POST", url, json=chat_body(messages), timeout=120.0) as response:
        response.raise_for_status()  # 404 / 500 -> HTTPStatusError
        for line in response.iter_lines():
            text = chunk_text(line)
            if text:  # skip "" (blank lines and the last "done" line)
                yield text
