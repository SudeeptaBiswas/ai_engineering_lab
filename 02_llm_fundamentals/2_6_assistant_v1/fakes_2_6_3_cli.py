"""Fakes for exercises_2_6_3_cli.py: the lines a "user" types + a fake model. Not a test file.

pytest only collects test_* / examples_* / exercises_* files.
"""

from collections.abc import Iterator
from typing import Any

import httpx
import pytest

import assistant.chat_turn as chat_turn_module
from assistant.memory import Message
from assistant.ollama_client import StreamPiece


class FakeModel:
    """Stands in for stream_reply: answers "Answer 1", "Answer 2", ... and never asks for tools.

    It keeps a copy of the messages of every call, so a test can check what was sent.
    """

    def __init__(self, fail_first_call: bool = False) -> None:
        """Start with no calls.

        Args:
            fail_first_call: True = the first call raises httpx.ConnectError (Ollama off).
        """
        self.sent_messages_per_call: list[list[Message]] = []  # one list of messages per call
        self.fail_first_call = fail_first_call

    def stream_reply(self, chat_messages: list[Message], tool_specs: list[dict[str, Any]]) -> Iterator[StreamPiece]:
        """Same parameters as the real stream_reply. Hands out "Answer" then " N".

        Args:
            chat_messages: what the chat sends.
            tool_specs: the tools offered (not used here).
        Returns:
            A generator of 2 text pieces.
        """
        self.sent_messages_per_call.append(list(chat_messages))  # list(...) = a copy
        call_number = len(self.sent_messages_per_call)
        if self.fail_first_call and call_number == 1:
            raise httpx.ConnectError("Ollama is not running")
        yield StreamPiece(text="Answer")
        yield StreamPiece(text=f" {call_number}")


def use_fakes(monkeypatch: pytest.MonkeyPatch, typed_lines: list[str], fail_first_call: bool = False) -> FakeModel:
    """Swap input() and stream_reply for fakes.

    After the last typed line, input() raises EOFError, like Ctrl+Z / Ctrl+D
    in a real terminal.
    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        typed_lines: what the "user" types, in order, e.g. ["hi", "/exit"].
        fail_first_call: passed on to FakeModel.
    Returns:
        The FakeModel, to look at .sent_messages_per_call afterwards.
    """
    lines_left = list(typed_lines)  # a copy we can take lines from
    fake_model = FakeModel(fail_first_call)

    def fake_input(input_prompt: str = "") -> str:
        """Stand in for input(): hand out the next typed line.

        Args:
            input_prompt: e.g. "you> " (not shown).
        Returns:
            The next typed line.
        """
        if len(lines_left) == 0:
            raise EOFError
        next_line = lines_left.pop(0)
        return next_line

    monkeypatch.setattr("builtins.input", fake_input)  # input() lives in the builtins module
    monkeypatch.setattr(chat_turn_module, "stream_reply", fake_model.stream_reply)  # where chat_turn looks it up
    return fake_model


def message_texts(chat_messages: list[Message]) -> list[str]:
    """Take just the texts of one call's messages.

    Args:
        chat_messages: e.g. fake_model.sent_messages_per_call[0].
    Returns:
        e.g. [SYSTEM_PROMPT, "hi"].
    """
    texts: list[str] = []
    for message in chat_messages:
        texts.append(message["content"])
    return texts
