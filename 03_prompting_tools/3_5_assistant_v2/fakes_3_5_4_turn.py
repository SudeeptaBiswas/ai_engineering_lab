"""Fakes for test_3_5_4_turn.py: a model that follows a script, and a spy on run_tool. Not a test file.

pytest only collects test_* / examples_* / exercises_* files.
"""

from collections.abc import Iterator
from typing import Any

import pytest

import assistant.chat_turn as chat_turn_module
from assistant.memory import Message
from assistant.ollama_client import StreamPiece
from assistant.tool_runner import run_tool
from lab_tools.log import debug, log


class ScriptedModel:
    """Stands in for stream_reply: call 1 hands out script[0], call 2 script[1], and so on.

    It keeps a copy of the messages of every call, so a test can check what was sent.
    """

    def __init__(self, scripted_replies: list[list[StreamPiece]]) -> None:
        """Remember the script.

        Args:
            scripted_replies: one list of stream pieces per model call.
        """
        self.scripted_replies = scripted_replies
        self.sent_messages_per_call: list[list[Message]] = []

    @debug
    def stream_reply(self, chat_messages: list[Message], tool_specs: list[dict[str, Any]]) -> Iterator[StreamPiece]:
        """Same parameters as the real stream_reply. Hands out the next scripted reply.

        Args:
            chat_messages: what the chat sends.
            tool_specs: the tools offered (not used here).
        Returns:
            A generator of the scripted pieces for this call.
        """
        self.sent_messages_per_call.append(list(chat_messages))  # list(...) = a copy
        call_index = len(self.sent_messages_per_call) - 1  # 0 for the first call
        scripted_reply = self.scripted_replies[call_index]
        log.debug("fake call %d: %d messages -> %s", call_index + 1, len(chat_messages), scripted_reply)
        for stream_piece in scripted_reply:
            yield stream_piece


@debug
def use_scripted_model(monkeypatch: pytest.MonkeyPatch, scripted_replies: list[list[StreamPiece]]) -> ScriptedModel:
    """Swap stream_reply in chat_turn for a ScriptedModel.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        scripted_replies: one list of stream pieces per model call.
    Returns:
        The ScriptedModel, to look at .sent_messages_per_call afterwards.
    """
    log.debug("start: %d scripted calls", len(scripted_replies))
    scripted_model = ScriptedModel(scripted_replies)
    monkeypatch.setattr(chat_turn_module, "stream_reply", scripted_model.stream_reply)  # where chat_turn looks it up
    return scripted_model


@debug
def spy_on_run_tool(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Write down the name of every tool that really runs; the tools still run as normal.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    Returns:
        A list that fills up with tool names, e.g. ["order_status"].
    """
    tools_that_ran: list[str] = []

    @debug
    def run_tool_and_note_it(tool_name: str, tool_arguments: dict[str, Any]) -> str:
        """Note the tool name, then run the real tool.

        Args:
            tool_name: e.g. "order_status".
            tool_arguments: e.g. {"order_id": "A-1001"}.
        Returns:
            The real tool's result text.
        """
        tools_that_ran.append(tool_name)
        tool_result_text = run_tool(tool_name, tool_arguments)
        log.debug("noted %s; tools_that_ran=%s", tool_name, tools_that_ran)
        return tool_result_text

    monkeypatch.setattr(chat_turn_module, "run_tool", run_tool_and_note_it)
    log.debug("result: run_tool is now watched")
    return tools_that_ran
