"""The gate: code decides if a tool call may run, before it runs (lesson 3.4).

Why: text in a tool result or a message can talk the model into calling a
tool (3.4 part 2: refund(A-1001, 500) ran although the prompt said "only
refund when the customer asks"). A prompt can't stop that; code can.

Rules:
  read-only tool           -> always runs
  tool that changes data   -> refund only: the customer's own question must ask
                              for a refund, and the amount must be 0 to 50
  unknown tool             -> blocked

Tests: 03_prompting_tools/3_5_assistant_v2/test_3_5_2_gate.py
"""

from typing import Any

from assistant.tools import TOOLS_BY_NAME
from lab_tools.log import cut_text, debug, log

MAX_REFUND_WITHOUT_HUMAN = 50  # larger refunds need a person to confirm
REFUND_REQUEST_WORD = "refund"  # must appear in the customer's own question


@debug
def find_refund_problem(tool_arguments: dict[str, Any], user_question: str) -> str | None:
    """Check a refund call against the refund rules.

    How:
        1. The customer's question must contain "refund" (any case).
        2. The amount must be a number (a missing amount was a crash in 3.4).
        3. The amount must be at most MAX_REFUND_WITHOUT_HUMAN.
    Args:
        tool_arguments: what the model sent, e.g. {"order_id": "A-1001", "amount": 500}.
        user_question: the customer's message this turn, e.g. "Where is my order A-1001?".
    Returns:
        None = OK, or the reason, e.g. "refund needs a human: 500 is over 50".
    """
    log.debug("start: %s user_question=%s", tool_arguments, cut_text(user_question))
    question_lower = user_question.lower()
    customer_asked_for_refund = REFUND_REQUEST_WORD in question_lower
    refund_amount = tool_arguments.get("amount")  # None if the model left it out
    # bool is a kind of int in Python (True == 1), so rule it out on its own
    is_bool = isinstance(refund_amount, bool)
    is_number = isinstance(refund_amount, (int, float)) and not is_bool
    log.debug("customer_asked_for_refund=%s amount=%r is_number=%s", customer_asked_for_refund,
              refund_amount, is_number)
    refund_problem: str | None = None
    if not customer_asked_for_refund:
        refund_problem = "refund needs a human: the customer did not ask for one"
    elif is_bool or not isinstance(refund_amount, (int, float)):  # = not is_number; isinstance tells pyright the type
        refund_problem = f"refund needs a human: amount {refund_amount!r} is not a number"
    elif refund_amount > MAX_REFUND_WITHOUT_HUMAN:
        refund_problem = f"refund needs a human: {refund_amount} is over {MAX_REFUND_WITHOUT_HUMAN}"
    log.debug("result: %s", refund_problem)
    return refund_problem


@debug
def find_reason_to_block(tool_name: str, tool_arguments: dict[str, Any], user_question: str) -> str | None:
    """Decide if a tool call may run. None = run it; else the reason it is blocked.

    How:
        1. Unknown tool -> blocked.
        2. Read-only tool -> runs.
        3. refund -> find_refund_problem.
    Args:
        tool_name: e.g. "refund".
        tool_arguments: what the model sent, e.g. {"order_id": "A-1001", "amount": 500}.
        user_question: the customer's message this turn.
    Returns:
        None, or e.g. "refund needs a human: the customer did not ask for one".
    """
    log.debug("start: %s(%s) user_question=%s", tool_name, tool_arguments, cut_text(user_question))
    tool = TOOLS_BY_NAME.get(tool_name)
    block_reason: str | None = None
    if tool is None:
        block_reason = f"unknown tool: {tool_name}"
    elif not tool.changes_data:
        block_reason = None  # read-only: safe to run
    elif tool_name == "refund":
        block_reason = find_refund_problem(tool_arguments, user_question)
    else:
        block_reason = f"{tool_name} changes data and has no rule yet: needs a human"
    log.debug("result: block_reason=%s", block_reason)
    return block_reason
