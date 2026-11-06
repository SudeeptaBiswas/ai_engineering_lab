"""Replace each `...` with code. Run until every line says PASS.
Needs Ollama running with qwen3:1.7b pulled (`ollama list`)."""

import json  # pyright: ignore[reportUnusedImport] — json.loads for stream lines
from typing import Any  # "any type": what json.loads returns. Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until you use it

from lab_tools.check import check  # numbered PASS/FAIL + path:line links
from lab_tools.log import debug, log  # pyright: ignore[reportUnusedImport]

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows
MODEL = "qwen3:1.7b"  # with think=False: ~2.5 s per short answer (LESSON 2.3)

Message = dict[str, str]  # type alias: {"role": ..., "content": ...}


# ---------- Messages (no HTTP) ----------
def message(role: str, content: str) -> Message:
    """{"role": role, "content": content}"""
    ...


def add_message(history: list[Message], role: str, content: str) -> list[Message]:
    """A NEW list: history + one message. Do not change `history` itself.
    Hint: list + list makes a new list."""
    ...


def chat_body(messages: list[Message], stream: bool, max_tokens: int) -> dict[str, Any]:
    """The JSON body for POST /api/chat: model MODEL, these messages, this
    stream flag, "think": False, and options {"num_predict": max_tokens}."""
    ...


# ---------- Stream lines (no HTTP) ----------
def chunk_text(line: str) -> str:
    """One stream line (a JSON object) -> the text in message.content."""
    ...


def join_chunks(lines: list[str]) -> str:
    """All stream lines -> the full answer. Skip empty lines."""
    ...


def tokens_per_second(last_line: str) -> float:
    """The last stream line has eval_count (tokens) and eval_duration
    (NANOseconds, 1 s = 1_000_000_000 ns). Return tokens / seconds, rounded to 1."""
    ...


# ---------- Real calls (Ollama) ----------
def ask(messages: list[Message], max_tokens: int = 60) -> str:
    """POST /api/chat with stream False -> the answer text."""
    ...


def stop_reason(messages: list[Message], max_tokens: int) -> str:
    """Same call, but return done_reason: "stop" (finished) or "length" (cut)."""
    ...


def ask_stream(messages: list[Message], max_tokens: int = 60) -> list[str]:
    """Stream the answer. Return the text of each chunk, in order, skipping
    empty ones. Hint: `with httpx.stream("POST", url, json=..., timeout=...)
    as response:` then `for line in response.iter_lines():`."""
    ...


# ---------- Test data: real lines from qwen3:1.7b (10284Sudee, 2026-11-06) ----------
TEST_LINES = [
    '{"model":"qwen3:1.7b","message":{"role":"assistant","content":"R"},"done":false}',
    '{"model":"qwen3:1.7b","message":{"role":"assistant","content":"AG"},"done":false}',
    "",
    '{"model":"qwen3:1.7b","message":{"role":"assistant","content":" helps"},"done":false}',
    '{"model":"qwen3:1.7b","message":{"role":"assistant","content":""},"done":true,'
    '"done_reason":"length","eval_count":30,"eval_duration":1844149000}',
]
SYSTEM = message("system", "Answer in one short sentence.")
COLOUR = [  # the model only "remembers" what is in this list
    SYSTEM,
    message("user", "My favourite colour is green."),
    message("assistant", "Nice, green is a calm colour."),
    message("user", "What is my favourite colour? Answer with one word."),
]


def _not_changed() -> bool:
    history = [SYSTEM]
    new_history = add_message(history, "user", "hi")
    return history == [SYSTEM] and len(new_history) == 2  # old one still 1 message?


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("message", lambda: message("user", "hi"), {"role": "user", "content": "hi"})
    check("add", lambda: len(add_message([SYSTEM], "user", "hi")), 2)
    check("add last", lambda: add_message([SYSTEM], "user", "hi")[-1]["content"], "hi")
    check("add no change", _not_changed, True)
    check("body", lambda: chat_body([SYSTEM], False, 5),
          {"model": MODEL, "messages": [SYSTEM], "stream": False, "think": False,
           "options": {"num_predict": 5}})
    check("chunk", lambda: chunk_text(TEST_LINES[1]), "AG")
    check("join", lambda: join_chunks(TEST_LINES), "RAG helps")
    check("speed", lambda: tokens_per_second(TEST_LINES[-1]), 16.3)
    check("ask", lambda: len(ask([SYSTEM, message("user", "Say hi.")])) > 0, True)
    check("cut short", lambda: stop_reason([SYSTEM, message("user", "Explain RAG.")], 5), "length")
    check("memory", lambda: "green" in ask(COLOUR, 10).lower(), True)
    check("stream parts", lambda: len(ask_stream([SYSTEM, message("user", "Say hi.")])) > 1, True)
