"""Check the final answer before it is kept: no refund claims without a real refund (lesson 3.4).

Why: the gate (tool_gate.py) only sees tool calls, not words. Measured
2026-11-15: in a long chat the model answered "The refund of $500.00 ...
has been recorded" without calling refund at all. Code checks what goes
out, the same way the gate checks what runs.

The answer is already on screen (streaming), so a false claim gets a
correction line, and memory keeps the corrected answer.

Tests: 03_prompting_tools/3_5_assistant_v2/test_3_5_5_answer_check.py
"""

from assistant.memory import Message
from lab_tools.log import cut_text, debug, log

REFUND_TOOL_NAME = "refund"
DONE_WORDS = ("processed", "recorded", "issued", "completed", "refunded", "approved")  # "it happened" words
CORRECTION_TEXT = ("Correction: no refund was made. Please ask for it again; "
                   "amounts over 50 need a human.")


def claims_refund_done(answer_text: str) -> bool:
    """Decide if an answer says a refund happened.

    How: the answer mentions "refund" AND one of DONE_WORDS, any case.
    It also fires on "has not been processed": harmless, because the check
    only acts when no refund ran, so the correction is true anyway.
    Args:
        answer_text: e.g. "The refund of $500.00 for order A-1002 has been recorded.".
    Returns:
        e.g. True.
    """
    answer_lower = answer_text.lower()
    mentions_refund = REFUND_TOOL_NAME in answer_lower
    has_done_word = False
    for done_word in DONE_WORDS:
        if done_word in answer_lower:
            has_done_word = True
    # --- explicit end ---
    # concise: has_done_word = any(done_word in answer_lower for done_word in DONE_WORDS)
    claims_done = mentions_refund and has_done_word
    return claims_done


def refund_really_ran(turn_messages: list[Message]) -> bool:
    """Look through this turn's tool results: did a refund run and succeed?

    How: a "tool" message from refund whose text does not start with
    "error:" (blocked calls and bad arguments both start with "error:").
    Args:
        turn_messages: all messages of this turn, tool results included.
    Returns:
        e.g. False when the gate blocked the refund.
    """
    refund_succeeded = False
    for message in turn_messages:
        is_refund_result = message["role"] == "tool" and message.get("tool_name") == REFUND_TOOL_NAME
        if is_refund_result and not message["content"].startswith("error:"):
            refund_succeeded = True
    return refund_succeeded


@debug
def correct_false_refund_claim(final_answer: str, turn_messages: list[Message]) -> str:
    """Return the answer to keep: unchanged, or with a correction if it claims a refund that never ran.

    How:
        1. No refund claim -> keep the answer.
        2. A refund really ran this turn -> keep the answer.
        3. Else -> print CORRECTION_TEXT and add it to the answer.
    Args:
        final_answer: the model's final text this turn.
        turn_messages: all messages of this turn, tool results included.
    Returns:
        e.g. "The refund ... has been recorded. Correction: no refund was made. ...".
    """
    claims_done = claims_refund_done(final_answer)
    really_ran = refund_really_ran(turn_messages)
    log.debug("start: answer=%s claims_done=%s really_ran=%s", cut_text(final_answer), claims_done, really_ran)
    if not claims_done or really_ran:
        log.debug("result: kept as is")
        return final_answer
    print(f"  ({CORRECTION_TEXT})")
    corrected_answer = f"{final_answer} {CORRECTION_TEXT}"
    log.debug("result: corrected")
    return corrected_answer
