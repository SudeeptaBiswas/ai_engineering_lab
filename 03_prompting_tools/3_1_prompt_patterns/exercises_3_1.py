"""Tests for prompts_3_1.py: 20 without Ollama + 2 real. They are the spec.

  uv run pytest 03_prompting_tools/3_1_prompt_patterns/exercises_3_1.py -v
Ollama off? Add -m "not ollama".
"""

from typing import Any

import httpx
import pytest

from prompts_3_1 import (EXAMPLES, LABELS, MODEL, SYSTEM_PROMPT, classify, few_shot_messages,
                         final_answer, parse_label, same_number, score)


# ---------- few_shot_messages ----------
def test_few_shot_order() -> None:
    """System first, each example as a user + assistant pair, question last."""
    shots = [("Refund please.", "billing"), ("Page is blank.", "bug")]
    assert few_shot_messages("Rules.", shots, "Dark mode?") == [
        {"role": "system", "content": "Rules."},
        {"role": "user", "content": "Refund please."},
        {"role": "assistant", "content": "billing"},
        {"role": "user", "content": "Page is blank."},
        {"role": "assistant", "content": "bug"},
        {"role": "user", "content": "Dark mode?"},
    ]


def test_few_shot_no_examples() -> None:
    """No examples = zero-shot with rules: just system + question."""
    assert few_shot_messages("Rules.", [], "Hi") == [
        {"role": "system", "content": "Rules."}, {"role": "user", "content": "Hi"}]


# ---------- parse_label ----------
# Real replies from qwen3:1.7b (lesson part 1) + the cleaning cases.
@pytest.mark.parametrize(("answer", "expected"), [
    ("billing", "billing"),
    (" Billing.\n", "billing"),
    ("**bug**", "bug"),
    ("The support ticket can be classified as a **Software Issue**.", None),
    ("refund", None),
    ("", None),
])
def test_parse_label(answer: str, expected: str | None) -> None:
    """Exact label after cleaning, else None.

    Args:
        answer: the model's reply.
        expected: the label, or None.
    """
    assert parse_label(answer, LABELS) == expected


# ---------- final_answer ----------
@pytest.mark.parametrize(("text", "expected"), [
    ("23 - 9 = 14\n14 + 36 = 50\n\nAnswer: 50", "50"),
    ("total 12.00\nanswer:   8.00  ", "8.00"),
    ("Answer: 95\nWait, 3/4 of 120 is 90.\nAnswer: 65", "65"),
    ("120 - (25) = 95", None),
])
def test_final_answer(text: str, expected: str | None) -> None:
    """Text of the last "Answer:" line, any case; None if there is none.

    Args:
        text: the model's reply.
        expected: what final_answer must return.
    """
    assert final_answer(text) == expected


# ---------- same_number ----------
@pytest.mark.parametrize(("got", "expected", "same"), [
    ("8.00", "8", True),
    ("95", "65", False),
    ("eight", "8", False),
    (None, "8", False),
])
def test_same_number(got: str | None, expected: str, same: bool) -> None:
    """Numbers compare by value; text or None is never a match.

    Args:
        got: parsed answer.
        expected: the right number as text.
        same: the result same_number must give.
    """
    assert same_number(got, expected) is same


# ---------- score ----------
def test_score_half() -> None:
    """1 of 2 right = 0.5."""
    assert score(["billing", "bug"], ["billing", "login"]) == 0.5


def test_score_empty() -> None:
    """Nothing to score = 0.0, not a ZeroDivisionError."""
    assert score([], []) == 0.0


def test_score_lengths_differ() -> None:
    """3 predictions for 2 answers is a bug in the caller: raise."""
    with pytest.raises(ValueError):
        score(["a", "b", "c"], ["a", "b"])


# ---------- classify, fake HTTP ----------
def test_classify_body_and_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sends the few-shot body at temperature 0 and parses " Billing." to "billing".

    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent_bodies: list[Any] = []

    def fake_post(url: str, **options: Any) -> httpx.Response:
        """Stand-in for httpx.post: saves the json= body, replies " Billing." (200)."""
        sent_bodies.append(options.get("json"))
        reply = {"message": {"role": "assistant", "content": " Billing."}, "done": True}
        return httpx.Response(200, json=reply, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    assert classify("Charged twice.") == "billing"
    assert sent_bodies == [{
        "model": MODEL,
        "messages": few_shot_messages(SYSTEM_PROMPT, EXAMPLES, "Charged twice."),
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "seed": 42, "num_predict": 20},
    }]


# ---------- classify, real Ollama ----------
@pytest.mark.ollama
@pytest.mark.parametrize(("ticket", "expected"), [
    ("I was charged twice for my subscription this month.", "billing"),
    ("After the update, the save button does nothing.", "bug"),
])
def test_classify_real(ticket: str, expected: str) -> None:
    """Two tickets the few-shot prompt got right in every measured run.

    Args:
        ticket: a ticket the model has not seen as an example.
        expected: its label.
    """
    assert classify(ticket) == expected
