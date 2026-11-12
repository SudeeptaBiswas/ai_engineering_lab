"""Tests for triage_3_2.py, part 2: triage() with fake HTTP (4) + real Ollama (2).

  uv run pytest 03_prompting_tools/3_2_structured_output/exercises_3_2_2_triage.py -v
Ollama off? Add -m "not ollama".
"""

import copy
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from triage_3_2 import SYSTEM_PROMPT, Triage, feedback, triage

GOOD = '{"label": "other", "priority": 2, "summary": "Add dark mode"}'

# ---------- triage, fake HTTP ----------
def fake_ollama(monkeypatch: pytest.MonkeyPatch, answers: list[str]) -> list[Any]:
    """Make httpx.post reply with these answers, in order; record each body sent.

    Args:
        monkeypatch: built-in pytest fixture.
        answers: model replies, one per call.
    Returns:
        The list the sent bodies go into (a spy, 1.9).
    """
    sent_bodies: list[Any] = []

    def fake_post(url: str, **options: Any) -> httpx.Response:
        """Stand-in for httpx.post: copy the body (triage keeps changing its list)."""
        sent_bodies.append(copy.deepcopy(options.get("json")))
        reply = {"message": {"role": "assistant", "content": answers[len(sent_bodies) - 1]}}
        return httpx.Response(200, json=reply, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent_bodies


def test_triage_first_try(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valid on try 1: one call, schema sent, Triage back.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent = fake_ollama(monkeypatch, [GOOD])
    assert triage("Dark mode?") == Triage(label="other", priority=2, summary="Add dark mode")
    assert len(sent) == 1
    assert sent[0]["messages"] == [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": "Dark mode?"}]
    assert sent[0]["format"] == Triage.model_json_schema()


def test_triage_cuts_fences(monkeypatch: pytest.MonkeyPatch) -> None:
    """A fenced reply is still valid after cut_out_json: no retry needed.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent = fake_ollama(monkeypatch, [f"```json\n{GOOD}\n```"])
    assert triage("Dark mode?") is not None
    assert len(sent) == 1


def test_triage_retry_sends_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bad then good: 2 calls; the 2nd has the bad reply + the feedback appended.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    bad = '{"label": "Feature", "priority": 2, "summary": "Add dark mode"}'
    sent = fake_ollama(monkeypatch, [bad, GOOD])
    assert triage("Dark mode?") is not None
    assert len(sent) == 2
    retry_messages = sent[1]["messages"]
    assert len(retry_messages) == 4
    assert retry_messages[2] == {"role": "assistant", "content": bad}
    with pytest.raises(ValidationError) as caught:  # the error triage() got
        Triage.model_validate_json(bad)
    assert retry_messages[3] == {"role": "user", "content": feedback(caught.value)}


def test_triage_gives_up(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bad every time: exactly max_tries calls, then None.

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent = fake_ollama(monkeypatch, ["no", "still no"])
    assert triage("Dark mode?", max_tries=2) is None
    assert len(sent) == 2


# ---------- triage, real Ollama ----------
@pytest.mark.ollama
@pytest.mark.parametrize(("ticket", "expected"), [
    ("I was charged twice for my subscription this month.", "billing"),
    ("My account is locked after three wrong tries.", "login"),
])
def test_triage_real(ticket: str, expected: str) -> None:
    """Two tickets the schema + fields prompt got right in every measured run.

    Args:
        ticket: a support ticket.
        expected: its label.
    """
    result = triage(ticket)
    assert result is not None
    assert result.label == expected
