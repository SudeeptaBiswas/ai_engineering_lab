"""Tests for assistant/tools.py + tool_runner.py: what the model is told, and running a tool. No Ollama.

  uv run pytest 03_prompting_tools/3_5_assistant_v2/test_3_5_1_tools.py -v
"""

from datetime import date
from typing import Any

import pytest

from assistant.tool_runner import build_tool_specs, run_tool
from lab_tools.log import debug, log


@debug
def find_tool_spec(tool_name: str) -> dict[str, Any]:
    """Pick one tool's spec by its name, so tests don't depend on the list order.

    Args:
        tool_name: e.g. "refund".
    Returns:
        e.g. {"type": "function", "function": {"name": "refund", ...}}.
    Raises:
        KeyError: no tool with that name.
    """
    for tool_spec in build_tool_specs():
        spec_name = tool_spec["function"]["name"]
        if spec_name == tool_name:
            log.debug("result: found %s", tool_name)
            return tool_spec
    log.debug("result: no tool %s", tool_name)
    raise KeyError(tool_name)


@debug
def test_tool_specs_list_all_four_tools_in_order() -> None:
    """The model is offered exactly the 4 tools, each as a "function": a missing one can't be called."""
    tool_specs = build_tool_specs()
    tool_names: list[str] = []
    tool_types: list[str] = []
    for tool_spec in tool_specs:
        tool_names.append(tool_spec["function"]["name"])
        tool_types.append(tool_spec["type"])
    expected_names = ["multiply", "order_status", "today", "refund"]
    log.debug("expected=%s got=%s types=%s", expected_names, tool_names, tool_types)
    assert tool_names == expected_names
    assert tool_types == ["function"] * 4


@pytest.mark.parametrize(("tool_name", "expected_fields"), [
    ("refund", ["amount", "order_id"]),                      # the money tool: both must be filled
    ("multiply", ["first_number", "second_number"]),         # names the model reads (were a / b)
])
@debug
def test_tool_spec_lists_the_fields_the_model_must_fill(tool_name: str, expected_fields: list[str]) -> None:
    """The spec's "required" list names every field: the model reads only this to fill the arguments.

    Args:
        tool_name: the tool to look at.
        expected_fields: its required fields, sorted.
    """
    tool_spec = find_tool_spec(tool_name)
    tool_parameters = tool_spec["function"]["parameters"]
    required_fields = sorted(tool_parameters["required"])
    log.debug("expected=%s got=%s", expected_fields, required_fields)
    assert required_fields == expected_fields


@pytest.mark.parametrize(("tool_name", "tool_arguments", "expected_result"), [
    ("multiply", {"first_number": 4821, "second_number": 3967}, "19124907"),          # whole number: no ".0"
    ("multiply", {"first_number": 2.5, "second_number": 3}, "7.5"),                    # decimals stay
    ("order_status", {"order_id": "A-1001"}, "shipped on 2026-11-10, arrives 2026-11-14"),  # a known order
    ("order_status", {"order_id": "1002"}, "waiting for payment"),                      # "1002" forgiven -> "A-1002"
    ("order_status", {"order_id": "A-9999"}, "error: no order A-9999"),                 # unknown order: text, not a crash
    ("refund", {"order_id": "A-1001", "amount": 20},
     "refund of 20.0 for order A-1001 recorded (fake: no money moved)"),                # fake: nothing is paid
])
@debug
def test_run_tool_gives_the_result_text(tool_name: str, tool_arguments: dict[str, Any], expected_result: str) -> None:
    """A good call runs the tool and returns its text: that text is all the model gets back.

    Args:
        tool_name: the tool the model asked for.
        tool_arguments: what the model sent.
        expected_result: the text the model should get back.
    """
    tool_result = run_tool(tool_name, tool_arguments)
    log.debug("expected=%r got=%r", expected_result, tool_result)
    assert tool_result == expected_result


@pytest.mark.parametrize(("tool_name", "tool_arguments", "expected_result"), [
    ("divide", {"first_number": 1, "second_number": 2}, "error: no tool 'divide'"),   # a made-up tool name
    ("multiply", {"first_number": 2}, "error: second_number: Field required"),         # missing argument
    ("multiply", {"first_number": 2, "second_number": 3, "c": 4},
     "error: c: Extra inputs are not permitted"),                                       # unknown argument
    ("multiply", {"a": 2, "b": 3},
     "error: first_number: Field required; second_number: Field required; "
     "a: Extra inputs are not permitted; b: Extra inputs are not permitted"),           # the old names
    ("order_status", {"order_id": "B-7"}, "error: order_id: Value error, order_id must look like A-1001"),  # bad id
])
@debug
def test_run_tool_turns_problems_into_error_text(tool_name: str, tool_arguments: dict[str, Any],
                                                 expected_result: str) -> None:
    """Bad calls never crash the chat; the model gets "error: ..." text and can try again.

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
    """today() answers in ISO form like 2026-11-15: the model can't know the date, and copies this text."""
    today_text = run_tool("today", {})
    parsed_date = date.fromisoformat(today_text)  # raises ValueError if the text is not YYYY-MM-DD
    log.debug("expected=%s got=%r", date.today(), today_text)
    assert parsed_date == date.today()
