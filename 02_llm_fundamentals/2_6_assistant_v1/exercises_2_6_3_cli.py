"""Tests for assistant/cli.py and plain chat turns: 7 with a fake model + 1 real.

  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_3_cli.py -v
Ollama off? Add -m "not ollama".
"""

import pytest

from assistant.chat_turn import answer_one_turn
from assistant.cli import MAX_HISTORY_TOKENS, SYSTEM_PROMPT, main
from assistant.memory import ChatMemory
from fakes_2_6_3_cli import message_texts, use_fakes  # typed lines + fake model
from lab_tools.log import debug, log


@debug
def test_answer_is_shown_returned_and_remembered(monkeypatch: pytest.MonkeyPatch,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    """One turn prints the answer, returns it, and saves question + answer: the next turn needs both.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        capsys: pytest's tool that captures print() output.
    """
    use_fakes(monkeypatch, [])
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    final_answer = answer_one_turn(memory, "hi")
    printed_text = capsys.readouterr().out
    remembered_texts = message_texts(memory.messages_to_send())
    log.debug("expected='Answer 1' got=%r; remembered=%s", final_answer, remembered_texts)
    assert final_answer == "Answer 1"
    assert "Answer 1" in printed_text
    assert remembered_texts == [SYSTEM_PROMPT, "hi", "Answer 1"]


@debug
def test_second_turn_sends_the_first_turn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn 2 sends turn 1's question AND answer: THE memory feature (the model itself remembers nothing).

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    fake_model = use_fakes(monkeypatch, ["My colour is green.", "What is my colour?", "/exit"])
    main()
    expected_texts = [SYSTEM_PROMPT, "My colour is green.", "Answer 1", "What is my colour?"]
    second_call_texts = message_texts(fake_model.sent_messages_per_call[1])
    log.debug("expected=%s got=%s", expected_texts, second_call_texts)
    assert len(fake_model.sent_messages_per_call) == 2
    assert second_call_texts == expected_texts


@pytest.mark.parametrize("exit_command", ["/exit", "/quit"])
@debug
def test_exit_command_stops_the_chat(monkeypatch: pytest.MonkeyPatch, exit_command: str) -> None:
    """After /exit (or /quit) nothing more is read or sent: the user can always stop the chat.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        exit_command: the word typed to quit.
    """
    fake_model = use_fakes(monkeypatch, [exit_command, "never sent"])
    main()
    log.debug("expected=0 calls got=%d", len(fake_model.sent_messages_per_call))
    assert fake_model.sent_messages_per_call == []


@debug
def test_empty_lines_send_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enter on an empty line (or only spaces) does not call the model: no wasted 5-second call.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    fake_model = use_fakes(monkeypatch, ["", "   ", "/exit"])
    main()
    log.debug("expected=0 calls got=%d", len(fake_model.sent_messages_per_call))
    assert fake_model.sent_messages_per_call == []


@debug
def test_piped_first_line_with_byte_order_mark_still_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    """A PowerShell pipe puts an invisible "\\ufeff" before line 1: "/exit" must still stop the chat.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    fake_model = use_fakes(monkeypatch, ["﻿/exit", "never sent"])
    main()
    log.debug("expected=0 calls got=%d", len(fake_model.sent_messages_per_call))
    assert fake_model.sent_messages_per_call == []


@debug
def test_reset_forgets_the_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    """After /reset the next call has only the rules + the new question: a fresh start, nothing old.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    fake_model = use_fakes(monkeypatch, ["first", "/reset", "second", "/exit"])
    main()
    second_call_texts = message_texts(fake_model.sent_messages_per_call[1])
    log.debug("expected=%s got=%s", [SYSTEM_PROMPT, "second"], second_call_texts)
    assert second_call_texts == [SYSTEM_PROMPT, "second"]


@debug
def test_end_of_input_ends_the_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ctrl+Z / Ctrl+D (EOFError from input) ends main() cleanly: piped input must not crash.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    fake_model = use_fakes(monkeypatch, ["hi"])  # no /exit: the next input() raises EOFError
    main()
    log.debug("expected=1 call got=%d", len(fake_model.sent_messages_per_call))
    assert len(fake_model.sent_messages_per_call) == 1


@debug
def test_ollama_down_prints_error_and_goes_on(monkeypatch: pytest.MonkeyPatch,
                                              capsys: pytest.CaptureFixture[str]) -> None:
    """An HTTP error prints a message and the chat keeps going: Ollama can restart, the chat survives.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        capsys: pytest's tool that captures print() output.
    """
    fake_model = use_fakes(monkeypatch, ["hi", "again", "/exit"], fail_first_call=True)
    main()
    printed_text = capsys.readouterr().out
    log.debug("expected=2 calls got=%d; printed=%r", len(fake_model.sent_messages_per_call), printed_text)
    assert len(fake_model.sent_messages_per_call) == 2
    assert "error" in printed_text.lower()


@pytest.mark.ollama
@debug
def test_real_model_remembers_turn_one() -> None:
    """With the real model, turn 2 uses what was said in turn 1: memory works end to end."""
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    answer_one_turn(memory, "My favourite colour is green.")
    second_answer = answer_one_turn(memory, "What is my favourite colour? One word.")
    log.debug("expected 'green' in %r", second_answer)
    assert "green" in second_answer.lower()
