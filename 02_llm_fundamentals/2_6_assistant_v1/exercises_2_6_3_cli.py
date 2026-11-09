"""Tests for assistant/cli.py: 7 with fakes + 1 real (Ollama).
Fill the stubs in assistant/cli.py until all pass.

  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_3_cli.py -v
Ollama off? Add -m "not ollama".
"""

import pytest

from assistant.cli import MAX_HISTORY_TOKENS, SYSTEM_PROMPT, answer, main
from assistant.memory import ChatMemory
from fakes_2_6_3_cli import sent_texts, use_fakes  # typed lines + fake model (read it)


# ---------- answer() ----------
def test_answer_prints_and_remembers(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """answer() shows the chunks, returns the full text, saves both messages.

    Args:
        monkeypatch: built-in pytest fixture.
        capsys: built-in fixture that captures print(). Java: a fake System.out.
    """
    use_fakes(monkeypatch, [])
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    assert answer(memory, "hi") == "Answer 1"
    assert "Answer 1" in capsys.readouterr().out
    assert sent_texts(memory.messages()) == [SYSTEM_PROMPT, "hi", "Answer 1"]


# ---------- main() ----------
def test_second_turn_sees_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE memory test: turn 2 sends turn 1's question AND answer.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    fake_model = use_fakes(monkeypatch, ["My colour is green.", "What is my colour?", "/exit"])
    main()
    assert len(fake_model.calls) == 2
    assert sent_texts(fake_model.calls[1]) == [
        SYSTEM_PROMPT, "My colour is green.", "Answer 1", "What is my colour?"]


@pytest.mark.parametrize("command", ["/exit", "/quit"])
def test_exit_stops(monkeypatch: pytest.MonkeyPatch, command: str) -> None:
    """After /exit (or /quit) nothing more is read or sent.

    Args:
        monkeypatch: built-in pytest fixture.
        command: the quit word typed.
    """
    fake_model = use_fakes(monkeypatch, [command, "never sent"])
    main()
    assert fake_model.calls == []


def test_blank_lines_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enter on an empty line (or spaces) sends nothing to the model.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    fake_model = use_fakes(monkeypatch, ["", "   ", "/exit"])
    main()
    assert fake_model.calls == []


def test_reset_forgets(monkeypatch: pytest.MonkeyPatch) -> None:
    """After /reset the next call has only the system prompt + the new question.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    fake_model = use_fakes(monkeypatch, ["first", "/reset", "second", "/exit"])
    main()
    assert sent_texts(fake_model.calls[1]) == [SYSTEM_PROMPT, "second"]


def test_end_of_input_quits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ctrl+Z / Ctrl+D (EOFError from input) ends main() cleanly, no crash.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    fake_model = use_fakes(monkeypatch, ["hi"])  # no /exit: input() then raises EOFError
    main()
    assert len(fake_model.calls) == 1


def test_ollama_down_keeps_going(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """An HTTP error prints a message; the chat goes on (no traceback).

    Args:
        monkeypatch: built-in pytest fixture.
        capsys: built-in fixture that captures print().
    """
    fake_model = use_fakes(monkeypatch, ["hi", "again", "/exit"], fail_first=True)
    main()
    assert len(fake_model.calls) == 2
    assert "error" in capsys.readouterr().out.lower()


# ---------- Real Ollama ----------
@pytest.mark.ollama
def test_real_model_remembers() -> None:
    """Two real turns through answer(): the model recalls turn 1."""
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    answer(memory, "My favourite colour is green.")
    assert "green" in answer(memory, "What is my favourite colour? One word.").lower()
