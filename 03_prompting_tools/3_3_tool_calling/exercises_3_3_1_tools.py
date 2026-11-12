"""Tests for tool_calls_3_3.py, part 1: tool_spec, chat_body, run_tool (no Ollama).

  uv run pytest 03_prompting_tools/3_3_tool_calling/exercises_3_3_1_tools.py -v
"""

from datetime import date
from typing import Any

import pytest

from tool_calls_3_3 import MODEL, chat_body, run_tool, tool_spec
from toolbox_3_3 import TOOLS, MultiplyArgs, NoArgs


# ---------- tool_spec ----------
def test_tool_spec_shape() -> None:
    """type "function"; name, description, parameters under "function"."""
    spec = tool_spec("multiply", TOOLS["multiply"])
    assert spec == {"type": "function", "function": {
        "name": "multiply",
        "description": "Multiply two numbers exactly, e.g. 4821 * 3967.",
        "parameters": MultiplyArgs.model_json_schema(),
    }}


def test_tool_spec_parameters_are_a_schema() -> None:
    """The parameters are a JSON Schema the model can read: both numbers required."""
    parameters = tool_spec("multiply", TOOLS["multiply"])["function"]["parameters"]
    assert parameters["type"] == "object"
    assert parameters["required"] == ["a", "b"]
    assert parameters["properties"]["a"]["type"] == "number"


def test_tool_spec_no_args() -> None:
    """A tool without arguments still sends an (empty) object schema."""
    spec = tool_spec("today", TOOLS["today"])
    assert spec["function"]["parameters"] == NoArgs.model_json_schema()
    assert spec["function"]["parameters"]["properties"] == {}


# ---------- chat_body ----------
def test_chat_body_fields() -> None:
    """Model, the same messages, no streaming, no thinking, fixed options, no format."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": "hi"}]
    body = chat_body(messages)
    assert body["model"] == MODEL
    assert body["messages"] == messages
    assert body["stream"] is False
    assert body["think"] is False
    assert body["options"] == {"temperature": 0, "seed": 42, "num_predict": 300}
    assert "format" not in body  # 3.2's knob; tools have their own schemas


def test_chat_body_tools() -> None:
    """Every tool in TOOLS, as tool_spec, in TOOLS order."""
    tools = chat_body([])["tools"]
    assert len(tools) == 3
    assert tools[0] == tool_spec("multiply", TOOLS["multiply"])
    names: list[str] = []
    for spec in tools:
        names.append(spec["function"]["name"])
    assert names == ["multiply", "order_status", "today"]


# ---------- run_tool ----------
@pytest.mark.parametrize(("name", "arguments", "expected"), [
    ("multiply", {"a": 4821, "b": 3967}, "19124907"),  # the model alone: 3 different answers in 3 runs
    ("multiply", {"a": 2.5, "b": 3}, "7.5"),
    ("multiply", {"a": "3", "b": "4"}, "12"),  # pydantic lax mode: "3" -> 3.0 (1.6)
    ("order_status", {"order_id": "A-1001"}, "shipped on 2026-11-10, arrives 2026-11-14"),
    ("order_status", {"order_id": "1002"}, "waiting for payment"),  # forgiven: A- added
    ("order_status", {"order_id": "A-9999"}, "error: no order A-9999"),  # the tool's own error
])
def test_run_tool_ok(name: str, arguments: dict[str, Any], expected: str) -> None:
    """Good arguments: the tool's own text comes back.

    Args:
        name: tool name.
        arguments: what the model sent.
        expected: the text run_tool returns.
    """
    assert run_tool(name, arguments) == expected


def test_run_tool_today() -> None:
    """No arguments -> today's date, as the model can't know it."""
    assert run_tool("today", {}) == date.today().isoformat()


def test_run_tool_unknown_name() -> None:
    """A tool the model made up: an error text, no exception."""
    assert run_tool("divide", {"a": 1, "b": 2}) == "error: no tool 'divide'"


@pytest.mark.parametrize(("name", "arguments", "expected"), [
    ("multiply", {"a": 2}, "error: b: Field required"),
    ("multiply", {"a": 2, "b": 3, "c": 4}, "error: c: Extra inputs are not permitted"),
    ("multiply", {}, "error: a: Field required; b: Field required"),
    ("order_status", {"order_id": "B-7"}, "error: order_id: Value error, order_id must look like A-1001"),
])
def test_run_tool_bad_arguments(name: str, arguments: dict[str, Any], expected: str) -> None:
    """Bad arguments: "error: " + every problem, "; " between them. No exception.

    Args:
        name: tool name.
        arguments: what the model sent.
        expected: the error text the model gets back.
    """
    assert run_tool(name, arguments) == expected
