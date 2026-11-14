"""Tests for assistant/tools.py + tool_runner.py: what the model is told, and running a tool. No Ollama.

  uv run pytest 03_prompting_tools/3_5_assistant_v2/test_3_5_1_tools.py -v
"""

from typing import Any

import pytest

from assistant.tool_runner import build_tool_specs, run_tool
from lab_tools.log import debug, log


@debug
def test_tool_specs_list_all_four_tools_in_order() -> None:
    """Checks: the model is offered exactly the 4 tools, each as a "function" with its name."""
    tool_specs = build_tool_specs()
    tool_names: list[str] = []
    for tool_spec in tool_specs:
        tool_names.append(tool_spec["function"]["name"])
    expected_names = ["multiply", "order_status", "today", "refund"]
    log.debug("expected=%s got=%s", expected_names, tool_names)
    assert tool_names == expected_names
    assert tool_specs[0]["type"] == "function"


@debug
def test_tool_spec_parameters_are_the_arguments_schema() -> None:
    """Checks: refund's parameters say which fields the model must fill (the model reads only this)."""
    tool_specs = build_tool_specs()
    refund_spec = tool_specs[3]  # order: multiply, order_status, today, refund
    refund_parameters = refund_spec["function"]["parameters"]
    required_fields = refund_parameters["required"]
    log.debug("expected=['order_id', 'amount'] got=%s", required_fields)
    assert sorted(required_fields) == ["amount", "order_id"]


@pytest.mark.parametrize(("tool_name", "tool_arguments", "expected_result"), [
    ("multiply", {"a": 4821, "b": 3967}, "19124907"),                                  # whole number: no ".0"
    ("multiply", {"a": 2.5, "b": 3}, "7.5"),                                            # decimals stay
    ("order_status", {"order_id": "A-1001"}, "shipped on 2026-11-10, arrives 2026-11-14"),
    ("order_status", {"order_id": "1002"}, "waiting for payment"),                      # "1002" forgiven -> "A-1002"
    ("order_status", {"order_id": "A-9999"}, "error: no order A-9999"),                 # unknown order: text, not a crash
    ("refund", {"order_id": "A-1001", "amount": 20},
     "refund of 20.0 for order A-1001 recorded (fake: no money moved)"),                # fake: nothing is paid
])
@debug
def test_run_tool_gives_the_result_text(tool_name: str, tool_arguments: dict[str, Any], expected_result: str) -> None:
    """Checks: a good call runs the tool and returns its text.

    Args:
        tool_name: the tool the model asked for.
        tool_arguments: what the model sent.
        expected_result: the text the model should get back.
    """
    tool_result = run_tool(tool_name, tool_arguments)
    log.debug("expected=%r got=%r", expected_result, tool_result)
    assert tool_result == expected_result


@pytest.mark.parametrize(("tool_name", "tool_arguments", "expected_result"), [
    ("divide", {"a": 1, "b": 2}, "error: no tool 'divide'"),                            # a made-up tool name
    ("multiply", {"a": 2}, "error: b: Field required"),                                 # missing argument
    ("multiply", {"a": 2, "b": 3, "c": 4}, "error: c: Extra inputs are not permitted"),  # unknown argument
    ("order_status", {"order_id": "B-7"}, "error: order_id: Value error, order_id must look like A-1001"),
])
@debug
def test_run_tool_turns_problems_into_error_text(tool_name: str, tool_arguments: dict[str, Any],
                                                 expected_result: str) -> None:
    """Checks: bad calls never crash the chat; the model gets "error: ..." text instead.

    Args:
        tool_name: the tool the model asked for.
        tool_arguments: what the model sent.
        expected_result: the error text the model should get back.
    """
    tool_result = run_tool(tool_name, tool_arguments)
    log.debug("expected=%r got=%r", expected_result, tool_result)
    assert tool_result == expected_result


@debug
def test_today_gives_an_iso_date() -> None:
    """Checks: today() answers like 2026-11-15 (the date itself changes every day)."""
    today_text = run_tool("today", {})
    log.debug("got=%r", today_text)
    assert len(today_text) == 10
    assert today_text[4] == "-" and today_text[7] == "-"
