"""Part 2 of 2: two Python tools the assistant uses. No Ollama needed.

Run:
  uv run python 02_llm_fundamentals/2_6_assistant_v1/examples_2_6_2_yield.py

  1. TypedDict: a dict whose keys pyright knows. Java: a record.
  2. Generators (yield): hand out values one by one. Java: an Iterator.
"""

import json  # json.loads: text -> dict (lesson 1.7)
from collections.abc import Iterator  # the type of what a generator returns
from typing import TypedDict


# ---------- 1. TypedDict ----------
# Until now a message was dict[str, str]: any keys allowed, so a typo like
# {"role": "user", "contnet": "hi"} passed pyright and failed at Ollama.
# Java: record Message(String role, String content) {}
class Message(TypedDict):
    """One chat message. At runtime a plain dict; only pyright sees the class."""

    role: str  # "system", "user" or "assistant"
    content: str  # the text


def show_typed_dict() -> None:
    """Build a Message: it is a normal dict, but pyright checks its keys."""
    greeting: Message = {"role": "user", "content": "hi"}
    # greeting = {"role": "user", "contnet": "hi"}  # pyright: error, no key "contnet"
    print("  value:", greeting, "| real type:", type(greeting).__name__)  # dict


# ---------- 2. Generators ----------
# A function with `yield` does not run when called. It returns a generator.
# Each loop step runs the body up to the next `yield`, hands out that value,
# and pauses there. Java: an Iterator whose next() runs until the next value.
def count_up(limit: int) -> Iterator[int]:
    """Hand out 1, 2, ... limit, printing when each one is made.

    Args:
        limit: e.g. 3.
    Returns:
        A generator giving 1, 2, 3.
    """
    for number in range(1, limit + 1):
        print(f"    making {number}")
        yield number  # pause here; the loop below gets `number`


def show_lazy() -> None:
    """Shows 'making' and 'got' taking turns: values are made on demand."""
    numbers = count_up(3)  # nothing printed yet: the body has not started
    for number in numbers:
        print(f"    got {number}")
    # One pass only, like a Java Iterator: a second loop gets nothing.
    leftover: list[int] = []
    for number in numbers:
        leftover.append(number)
    print("    second loop got:", leftover)  # []


# ---------- 3. The assistant's case: stream lines -> text chunks ----------
# Real lines from qwen3:1.7b (lesson 2.3). The last one has content "".
STREAM_LINES = [
    '{"message":{"role":"assistant","content":"R"},"done":false}',
    '{"message":{"role":"assistant","content":"AG"},"done":false}',
    "",
    '{"message":{"role":"assistant","content":" helps"},"done":false}',
    '{"message":{"role":"assistant","content":""},"done":true,"done_reason":"stop"}',
]


def text_chunks(lines: list[str]) -> Iterator[str]:
    """Yield the answer text of each stream line, skipping empty ones.

    stream_chat() in assistant/ has this shape, reading lines from Ollama.
    Args:
        lines: NDJSON lines, e.g. STREAM_LINES.
    Returns:
        A generator giving "R", "AG", " helps".
    """
    for line in lines:
        if not line.strip():  # blank line: nothing to parse
            continue
        text = json.loads(line)["message"]["content"]
        if text:  # the last line's "" is not a chunk (the 2.3 bug)
            yield text


def show_stream() -> None:
    """Print chunks as they come, like the chatbot; join them at the end."""
    parts: list[str] = []
    print("    bot> ", end="")
    for chunk in text_chunks(STREAM_LINES):
        print(chunk, end="", flush=True)  # no newline, show now (lesson 2.3)
        parts.append(chunk)
    print()
    full_answer = "".join(parts)  # "" + "R" + "AG" + " helps". Java: String.join("", parts)
    print("    saved to memory:", repr(full_answer), "from", parts)


if __name__ == "__main__":
    print("1. TypedDict:")
    show_typed_dict()
    print("2. Generator, made on demand:")
    show_lazy()
    print("3. Stream lines -> chunks:")
    show_stream()
