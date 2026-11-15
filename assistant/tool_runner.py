"""Tell the model which tools exist, and run the one it asks for (lesson 3.3).

Running never crashes the chat: every problem comes back as "error: ..."
text, which goes to the model as the tool's result. The model then decides
what to tell the user.

Tests: 03_prompting_tools/3_5_assistant_v2/test_3_5_1_tools.py
"""

from typing import Any

from pydantic import ValidationError

from assistant.tools import TOOLS_BY_NAME, Tool
from lab_tools.log import debug, log


@debug
def build_tool_spec(tool_name: str, tool: Tool) -> dict[str, Any]:
    """Describe one tool the way Ollama's "tools" list wants it.

    Args:
        tool_name: e.g. "order_status".
        tool: e.g. TOOLS_BY_NAME["order_status"].
    Returns:
        {"type": "function", "function": {"name": ..., "description": ...,
         "parameters": the arguments model as a JSON Schema (3.2)}}.
    """
    arguments_schema = tool.arguments_model.model_json_schema()  # the model reads this to fill the arguments
    function_part = {"name": tool_name, "description": tool.description, "parameters": arguments_schema}
    tool_spec: dict[str, Any] = {"type": "function", "function": function_part}
    log.debug("result: %s fields=%s", tool_name, list(arguments_schema.get("properties", {})))
    return tool_spec


@debug
def build_tool_specs() -> list[dict[str, Any]]:
    """Describe every tool in TOOLS_BY_NAME, in order, for the request body.

    Returns:
        4 tool specs: multiply, order_status, today, refund.
    """
    tool_specs: list[dict[str, Any]] = []
    for tool_name, tool in TOOLS_BY_NAME.items():
        tool_spec = build_tool_spec(tool_name, tool)
        tool_specs.append(tool_spec)
    log.debug("result: %d tool specs", len(tool_specs))
    return tool_specs


@debug
def describe_validation_problems(validation_error: ValidationError) -> str:
    """Turn pydantic's error list into one short line the model can read.

    Args:
        validation_error: e.g. from MultiplyArguments.model_validate({"first_number": 2}).
    Returns:
        e.g. "second_number: Field required" (several problems joined by "; ").
    """
    problem_texts: list[str] = []
    for problem in validation_error.errors():
        location_parts: list[str] = []
        for location_part in problem["loc"]:  # e.g. ("second_number",) or ("items", 0)
            location_parts.append(str(location_part))
        field_location = ".".join(location_parts)  # e.g. "second_number" or "items.0"
        problem_message = problem["msg"]  # e.g. "Field required"
        problem_texts.append(f"{field_location}: {problem_message}")
    problems_line = "; ".join(problem_texts)
    log.debug("result: %s", problems_line)
    return problems_line


@debug
def run_tool(tool_name: str, tool_arguments: dict[str, Any]) -> str:
    """Run one tool the model asked for and return its result as text. Never raises.

    How:
        1. Unknown tool name -> "error: no tool '...'".
        2. Check the arguments with the tool's model -> problems as "error: ...".
        3. Run the tool's function with the checked arguments.
    Args:
        tool_name: e.g. "multiply".
        tool_arguments: what the model sent, e.g. {"first_number": 4821, "second_number": 3967}.
    Returns:
        e.g. "19124907", or "error: second_number: Field required".
    """
    log.debug("start: %s(%s)", tool_name, tool_arguments)
    tool = TOOLS_BY_NAME.get(tool_name)  # None if the model made up a name
    if tool is None:
        unknown_tool_text = f"error: no tool {tool_name!r}"  # !r adds quotes around the name
        log.debug("result: %s", unknown_tool_text)
        return unknown_tool_text
    try:
        checked_arguments = tool.arguments_model.model_validate(tool_arguments)
    except ValidationError as validation_error:
        bad_arguments_text = "error: " + describe_validation_problems(validation_error)
        log.debug("result: %s", bad_arguments_text)
        return bad_arguments_text
    tool_result_text = tool.function(checked_arguments)
    log.debug("result: %s", tool_result_text)
    return tool_result_text
