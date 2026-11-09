"""Fakes for exercises_2_6_3_cli.py (done for you): typed lines + a fake model.

Not a test file: pytest only collects test_*/examples_*/exercises_* files.
"""

from collections.abc import Iterator

import httpx
import pytest

import assistant.cli as cli_module
from assistant.memory import Message


class FakeModel:
    """Stands in for stream_chat: answers "Answer 1", "Answer 2", ... and
    keeps a copy of the messages each call got. Java: a hand-written stub."""

    def __init__(self, fail_first: bool = False) -> None:
        """Args:
            fail_first: True = the first call raises httpx.ConnectError (Ollama off).
        """
        self.calls: list[list[Message]] = []  # messages sent, one list per call
        self.fail_first = fail_first

    def stream_chat(self, messages: list[Message]) -> Iterator[str]:
        """Same parameters as the real one. Yields "Answer", " N".

        Args:
            messages: what the CLI sends.
        Returns:
            A generator of 2 chunks.
        """
        self.calls.append(list(messages))  # list(...) = a copy
        if self.fail_first and len(self.calls) == 1:
            raise httpx.ConnectError("Ollama is not running")
        yield "Answer"
        yield f" {len(self.calls)}"


def use_fakes(monkeypatch: pytest.MonkeyPatch, lines: list[str], fail_first: bool = False) -> FakeModel:
    """Swap input() and stream_chat for fakes. After `lines`, input() raises
    EOFError, like Ctrl+Z / Ctrl+D in a real terminal.

    Args:
        monkeypatch: built-in pytest fixture.
        lines: what the "user" types, in order, e.g. ["hi", "/exit"].
        fail_first: passed on to FakeModel.
    Returns:
        The FakeModel, to look at .calls afterwards.
    """
    typed = list(lines)
    fake_model = FakeModel(fail_first)

    def fake_input(prompt: str = "") -> str:
        """Stands in for input(): hands out the next line.

        Args:
            prompt: e.g. "you> " (not shown).
        Returns:
            The next typed line.
        """
        if not typed:
            raise EOFError
        return typed.pop(0)

    monkeypatch.setattr("builtins.input", fake_input)  # input() lives in builtins
    monkeypatch.setattr(cli_module, "stream_chat", fake_model.stream_chat)  # where cli looks it up
    return fake_model


def sent_texts(messages: list[Message]) -> list[str]:
    """Just the texts, e.g. [SYSTEM_PROMPT, "hi"].

    Args:
        messages: one call's messages.
    Returns:
        The contents, in order.
    """
    texts: list[str] = []
    for message in messages:
        texts.append(message["content"])
    return texts
