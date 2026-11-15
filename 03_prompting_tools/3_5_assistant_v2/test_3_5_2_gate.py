"""Tests for assistant/tool_gate.py: which tool calls may run without a human. No Ollama.

  uv run pytest 03_prompting_tools/3_5_assistant_v2/test_3_5_2_gate.py -v
"""

from typing import Any

import pytest

from assistant.tool_gate import find_reason_to_block
from lab_tools.log import debug, log


@pytest.mark.parametrize(("tool_name", "tool_arguments", "user_question"), [
    ("order_status", {"order_id": "A-1001"}, "Where is my order A-1001?"),  # read-only: always runs
    ("today", {}, "What day is it?"),                                       # read-only
    ("multiply", {"first_number": 2, "second_number": 3}, "2 times 3?"),    # read-only
    ("refund", {"order_id": "A-1001", "amount": 20}, "Please refund my order A-1001."),  # asked, small
    ("refund", {"order_id": "A-1001", "amount": 50}, "I want a refund."),   # 50 is the limit, not over it
    ("refund", {"order_id": "A-1001", "amount": 20}, "REFUND me now"),      # any case
])
@debug
def test_gate_lets_safe_calls_run(tool_name: str, tool_arguments: dict[str, Any], user_question: str) -> None:
    """Read-only tools, and small refunds the customer asked for, get None (= run it): the gate must not block help.

    Args:
        tool_name: the tool the model asked for.
        tool_arguments: what the model sent.
        user_question: the customer's message this turn.
    """
    block_reason = find_reason_to_block(tool_name, tool_arguments, user_question)
    log.debug("expected=None got=%r", block_reason)
    assert block_reason is None


@pytest.mark.parametrize(("tool_name", "tool_arguments", "user_question", "expected_reason"), [
    # 3.4 part 2, measured: a tool result asked for this, not the customer
    ("refund", {"order_id": "A-1001", "amount": 500}, "Where is my order A-1001?",
     "refund needs a human: the customer did not ask for one"),
    ("refund", {"order_id": "A-1001", "amount": 500}, "Refund A-1001 please.",
     "refund needs a human: 500 is over 50"),                                 # asked, but too much
    ("refund", {"order_id": "A-1001", "amount": 50.5}, "refund please",
     "refund needs a human: 50.5 is over 50"),                                # just over the limit
    # the 3.4 review bug: no amount used to crash the gate (KeyError)
    ("refund", {"order_id": "A-1001"}, "refund please",
     "refund needs a human: amount None is not a number"),
    ("refund", {"order_id": "A-1001", "amount": "20"}, "refund please",
     "refund needs a human: amount '20' is not a number"),                    # text, not a number
    ("refund", {"order_id": "A-1001", "amount": True}, "refund please",
     "refund needs a human: amount True is not a number"),                    # True would count as 1
    ("delete_order", {"order_id": "A-1001"}, "Delete my order.", "unknown tool: delete_order"),  # made-up tool
])
@debug
def test_gate_blocks_risky_calls_with_a_reason(tool_name: str, tool_arguments: dict[str, Any], user_question: str,
                                               expected_reason: str) -> None:
    """Everything else is blocked, with a reason: the model passes it on, so the customer knows why.

    Args:
        tool_name: the tool the model asked for.
        tool_arguments: what the model sent.
        user_question: the customer's message this turn.
        expected_reason: why it is blocked.
    """
    block_reason = find_reason_to_block(tool_name, tool_arguments, user_question)
    log.debug("expected=%r got=%r", expected_reason, block_reason)
    assert block_reason == expected_reason
