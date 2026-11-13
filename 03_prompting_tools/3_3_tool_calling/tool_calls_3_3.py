"""Lesson 3.3 exercises: raw tool calling over HTTP. YOU fill them.

Replace each `raise NotImplementedError` with code, until every test in
this folder passes (exercises_3_3_1_tools.py first, then _2_loop.py):
  uv run pytest 03_prompting_tools/3_3_tool_calling -v
Ollama off? Add -m "not ollama". The tools are in toolbox_3_3.py (given).
"""

from typing import Any  # "any type". Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until ask() uses it
from pydantic import ValidationError  # pyright: ignore[reportUnusedImport] — until run_tool() uses it

from toolbox_3_3 import TOOLS, Tool  # pyright: ignore[reportUnusedImport] — until chat_body() uses TOOLS

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
SYSTEM_PROMPT = ("You are a support assistant. Use a tool whenever one fits; "
                 "never guess numbers, dates or order details.")


def tool_spec(name: str, tool: Tool) -> dict[str, Any]:
    """One entry of the "tools" list Ollama reads.

    Args:
        name: e.g. "multiply".
        tool: e.g. TOOLS["multiply"].
    Returns:
        {"type": "function", "function": {"name": name, "description": ...,
         "parameters": the args model's JSON Schema (3.2)}}.
    """
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": tool.description,
            "parameters": tool.args_model.model_json_schema(),
        }
    }


def chat_body(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """The JSON body for POST /api/chat, with every tool in TOOLS.

    Always: model, messages, "stream": False, "think": False,
    "tools": [tool_spec(...) for each TOOLS entry, in order],
    "options": {"temperature": 0, "seed": 42, "num_predict": 300}.
    Args:
        messages: e.g. [system, user].
    Returns:
        The body dict, ready for httpx.post(..., json=body).
    """

    body = {"model": MODEL, "messages": messages, "stream": False, "think": False,
            "options": {"temperature": 0, "seed": 42, "num_predict": 300},
            "tools": [
                tool_spec(name, tool)
                for name, tool in TOOLS.items()
            ]}
    return body

def run_tool(name: str, arguments: dict[str, Any]) -> str:
    """Run one tool call. Never raises: problems come back as "error: ..." text.

    Unknown name -> "error: no tool 'divide'" (name with quotes: {name!r}).
    Bad arguments (ValidationError) -> "error: " + one "<where>: <msg>" per
    problem, joined by "; " (where = loc joined by ".", as in 3.2 feedback).
    Else -> the tool's function, given the checked args object.
    Hint: tool.args_model.model_validate(arguments) (1.6).
    Args:
        name: e.g. "multiply".
        arguments: e.g. {"a": 4821, "b": 3967}.
    Returns:
        e.g. "19124907", or "error: b: Field required".
    """
    tool = TOOLS.get(name)

    if tool is None:
        return f"error: no tool {name!r}"

    try:
        checked_args = tool.args_model.model_validate(arguments)
    except ValidationError as exc:
        problems = [
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        return "error: " + "; ".join(problems)

    try:
        return str(tool.function(checked_args))
    except Exception as exc:
        return f"error: {exc}"


def ask(question: str, max_rounds: int = 5) -> str | None:
    """Chat with tools until the model answers in text.

    messages = [system SYSTEM_PROMPT, user question]. Each round:
      POST {OLLAMA_URL}/api/chat, json=chat_body(messages), timeout 300,
      raise_for_status(), message = reply["message"]; append it AS IS.
      No "tool_calls" (or empty) -> return message["content"].
      Else, for each call: name + arguments from call["function"], append
      {"role": "tool", "tool_name": name, "content": run_tool(...)}.
    Args:
        question: e.g. "What is 4821 * 3967?".
        max_rounds: most POSTs, e.g. 5.
    Returns:
        The answer text. None if every round asked for tools.
    Raises:
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
    """
    messages: list[dict[str, Any]]  = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question},]
    for _ in range(max_rounds):
        response = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json=chat_body(messages),
            timeout=300,
        )
        response.raise_for_status()
        message = response.json()["message"]
        # messages.append(message)  # as is, tool_calls included
        calls: list[dict[str, Any]] = message.get("tool_calls") or []
        if not calls:
            return message["content"]
        for call in calls:
            name = call["function"]["name"]
            result = run_tool(name, call["function"]["arguments"])
            # print(f"    call {name}({call['function']['arguments']}) -> {result[:45]!r}")
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return None
