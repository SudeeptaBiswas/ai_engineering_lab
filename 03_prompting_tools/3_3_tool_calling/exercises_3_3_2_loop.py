"""Tests for tool_calls_3_3.py, part 2: ask() with fake HTTP (5) + real Ollama (2).

  uv run pytest 03_prompting_tools/3_3_tool_calling/exercises_3_3_2_loop.py -v
Ollama off? Add -m "not ollama".
"""

import copy
from typing import Any

import httpx
import pytest

from tool_calls_3_3 import SYSTEM_PROMPT, ask, chat_body


def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """One tool call, the shape Ollama sends (part 1 printed it).

    Args:
        name: e.g. "multiply".
        arguments: e.g. {"a": 7, "b": 6}.
    Returns:
        {"id": ..., "function": {"index": 0, "name": ..., "arguments": ...}}.
    """
    return {"id": "call_test", "function": {"index": 0, "name": name, "arguments": arguments}}


def fake_ollama(monkeypatch: pytest.MonkeyPatch, replies: list[dict[str, Any]]) -> list[Any]:
    """Make httpx.post reply with these "message" dicts, in order; record each body.

    Args:
        monkeypatch: built-in pytest fixture.
        replies: e.g. [{"role": "assistant", "content": "Paris."}].
    Returns:
        The list the sent bodies go into (a spy, 1.9).
    """
    sent_bodies: list[Any] = []

    def fake_post(url: str, **options: Any) -> httpx.Response:
        """Stand-in for httpx.post: copy the body (ask() keeps changing its list)."""
        sent_bodies.append(copy.deepcopy(options.get("json")))
        reply = {"message": replies[len(sent_bodies) - 1]}
        return httpx.Response(200, json=reply, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent_bodies


def test_ask_no_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    """No tool_calls: one POST, the text is the answer, the body has the tools.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent = fake_ollama(monkeypatch, [{"role": "assistant", "content": "Paris."}])
    assert ask("Capital of France?") == "Paris."
    assert len(sent) == 1
    first = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Capital of France?"}]
    assert sent[0] == chat_body(first)


def test_ask_one_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    """Call, then answer: the 2nd POST has the model's reply AS IS + a tool message.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    asks = {"role": "assistant", "content": "", "tool_calls": [call("multiply", {"a": 7, "b": 6})]}
    sent = fake_ollama(monkeypatch, [asks, {"role": "assistant", "content": "It is 42."}])
    assert ask("7 * 6?") == "It is 42."
    assert len(sent) == 2
    assert sent[1]["messages"][2:] == [asks, {"role": "tool", "tool_name": "multiply", "content": "42"}]


def test_ask_two_calls_in_one_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two calls in one reply (part 1, step 3): two tool messages, in order.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    calls = [call("multiply", {"a": 3, "b": 4}), call("order_status", {"order_id": "A-1002"})]
    asks = {"role": "assistant", "content": "", "tool_calls": calls}
    sent = fake_ollama(monkeypatch, [asks, {"role": "assistant", "content": "12; unpaid."}])
    assert ask("3 * 4 and order A-1002?") == "12; unpaid."
    assert sent[1]["messages"][3:] == [
        {"role": "tool", "tool_name": "multiply", "content": "12"},
        {"role": "tool", "tool_name": "order_status", "content": "waiting for payment"},
    ]


def test_ask_bad_arguments_go_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bad arguments don't crash the loop: the error text goes back to the model.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    asks = {"role": "assistant", "content": "", "tool_calls": [call("multiply", {"a": 7})]}
    sent = fake_ollama(monkeypatch, [asks, {"role": "assistant", "content": "Need b."}])
    assert ask("7 * ?") == "Need b."
    assert sent[1]["messages"][-1] == {"role": "tool", "tool_name": "multiply",
                                       "content": "error: b: Field required"}


def test_ask_gives_up(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tool calls every round: exactly max_rounds POSTs, then None.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    asks = {"role": "assistant", "content": "", "tool_calls": [call("today", {})]}
    sent = fake_ollama(monkeypatch, [asks, asks, asks])
    assert ask("Date?", max_rounds=3) is None
    assert len(sent) == 3


# ---------- real Ollama ----------
@pytest.mark.ollama
@pytest.mark.parametrize(("question", "expected"), [
    ("What is 4821 * 3967?", "19124907"),  # no tools: 3 different answers in 3 runs
    ("Where is my order A-1001?", "2026-11-14"),
])
def test_ask_real(question: str, expected: str) -> None:
    """Two questions the loop got right in every measured run.

    Args:
        question: needs a tool.
        expected: must be in the answer.
    """
    answer = ask(question)
    assert answer is not None
    assert expected in answer.replace(",", "")
