"""Tests for assistant/answer_check.py: no refund claims without a real refund. No Ollama.

  uv run pytest 03_prompting_tools/3_5_assistant_v2/test_3_5_5_answer_check.py -v
"""

import pytest

from assistant.answer_check import CORRECTION_TEXT, claims_refund_done, correct_false_refund_claim
from assistant.chat_turn import answer_one_turn
from assistant.cli import MAX_HISTORY_TOKENS, SYSTEM_PROMPT
from assistant.memory import ChatMemory, Message
from assistant.ollama_client import StreamPiece, ToolCall
from fakes_3_5_4_turn import use_scripted_model
from lab_tools.log import debug, log

# Measured 2026-11-15: the 5th question of a chat got this with NO refund call
FALSE_CLAIM = "The refund of $500.00 for order A-1002 has been recorded (fake: no money moved)."
REFUND_RAN: list[Message] = [{"role": "tool", "tool_name": "refund",
                              "content": "refund of 20.0 for order A-1001 recorded (fake: no money moved)"}]
REFUND_BLOCKED: list[Message] = [{"role": "tool", "tool_name": "refund",
                                  "content": "error: blocked: refund needs a human: 500 is over 50"}]
NO_TOOLS_RAN: list[Message] = []


@pytest.mark.parametrize(("answer_text", "expected_claim"), [
    (FALSE_CLAIM, True),                                              # the measured case
    ("Your refund has been processed.", True),                        # another "done" word
    ("I REFUNDED order A-1001.", True),                               # any case
    ("Your order A-1001 arrives on 2026-11-14.", False),              # no refund talk
    ("I cannot refund that. Please ask a human.", False),             # refund, but no "done" word
])
@debug
def test_claims_refund_done_spots_done_words(answer_text: str, expected_claim: bool) -> None:
    """Checks: "refund" + a "done" word = a claim; refund talk without one is not.

    Args:
        answer_text: the model's answer.
        expected_claim: does it say a refund happened?
    """
    claim_found = claims_refund_done(answer_text)
    log.debug("expected=%s got=%s for %r", expected_claim, claim_found, answer_text)
    assert claim_found is expected_claim


@pytest.mark.parametrize(("turn_messages", "expected_answer"), [
    (NO_TOOLS_RAN, f"{FALSE_CLAIM} {CORRECTION_TEXT}"),    # claim, no refund call: corrected
    (REFUND_BLOCKED, f"{FALSE_CLAIM} {CORRECTION_TEXT}"),  # claim, but the gate blocked it: corrected
    (REFUND_RAN, FALSE_CLAIM),                             # a refund really ran: the claim is true, kept
])
@debug
def test_false_claim_gets_a_correction(turn_messages: list[Message], expected_answer: str) -> None:
    """Checks: the correction is added only when no refund succeeded this turn.

    Args:
        turn_messages: this turn's tool results.
        expected_answer: the answer to keep.
    """
    checked_answer = correct_false_refund_claim(FALSE_CLAIM, turn_messages)
    log.debug("expected=%r got=%r", expected_answer, checked_answer)
    assert checked_answer == expected_answer


@debug
def test_answer_without_claim_is_kept_as_is() -> None:
    """Checks: a normal answer passes untouched, even with no tools run."""
    normal_answer = "Your order A-1001 arrives on 2026-11-14."
    checked_answer = correct_false_refund_claim(normal_answer, NO_TOOLS_RAN)
    log.debug("expected=%r got=%r", normal_answer, checked_answer)
    assert checked_answer == normal_answer


@debug
def test_turn_with_false_claim_is_corrected_in_memory(monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture[str]) -> None:
    """Checks the whole turn: the model claims a refund without calling the tool; the user sees
    a correction and memory keeps the corrected answer (so later turns don't copy the claim).

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
        capsys: pytest's tool that captures print() output.
    """
    use_scripted_model(monkeypatch, [[StreamPiece(text=FALSE_CLAIM)]])
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    answer_one_turn(memory, "Refund order A-1002, amount 500.")
    printed_text = capsys.readouterr().out
    remembered_messages = memory.messages_to_send()
    remembered_answer = remembered_messages[-1]["content"]
    log.debug("remembered_answer=%r", remembered_answer)
    assert CORRECTION_TEXT in printed_text
    assert remembered_answer == f"{FALSE_CLAIM} {CORRECTION_TEXT}"


@debug
def test_turn_with_real_refund_is_not_corrected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Checks the whole turn: a small refund the customer asked for runs, so its claim stays.

    Args:
        monkeypatch: pytest's tool to swap functions for one test.
    """
    small_refund = StreamPiece(text="", tool_calls=[ToolCall("refund", {"order_id": "A-1001", "amount": 20})])
    true_claim = "The refund of $20 for order A-1001 has been recorded."
    use_scripted_model(monkeypatch, [[small_refund], [StreamPiece(text=true_claim)]])
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    final_answer = answer_one_turn(memory, "Please refund my order A-1001, 20 dollars.")
    log.debug("expected=%r got=%r", true_claim, final_answer)
    assert final_answer == true_claim
