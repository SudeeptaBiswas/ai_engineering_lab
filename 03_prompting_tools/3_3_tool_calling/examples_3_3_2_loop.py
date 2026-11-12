"""Part 2 of 2: the tool loop, 3 tools, and what the description does.

Run (~2 min, needs Ollama + qwen3:1.7b):
  uv run python 03_prompting_tools/3_3_tool_calling/examples_3_3_2_loop.py

  1. loop      : call tools until the model answers in text; 8 questions
  2. wording   : the same order tool, described 3 ways
  3. forgiving : the tool accepts "1001" as "A-1001"
"""

import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()
from datetime import date
from typing import Any  # "any type". Java: Object

import httpx  # HTTP client (1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
SYSTEM_PROMPT = ("You are a support assistant. Use a tool whenever one fits; "
                 "never guess numbers, dates or order details.")
ORDERS = {"A-1001": "shipped on 2026-11-10, arrives 2026-11-14", "A-1002": "waiting for payment"}
ORDER_ID = {"type": "string"}
ORDER_ID_DESCRIBED = {"type": "string", "description": "Like A-1001. Digits only, e.g. 1002, mean A-1002."}
QUESTIONS = [  # (question, words the answer must hold)
    ("What is 4821 * 3967?", ["19124907"]),
    ("How much is 239 times 571?", ["136469"]),
    ("Where is my order A-1001?", ["2026-11-14"]),
    ("Where is my order 1002?", ["payment"]),
    ("What is today's date?", ["2026"]),
    ("Where is order A-1002 and what is 3 * 4?", ["payment", "12"]),
    ("What is the capital of France?", ["Paris"]),
    ("Say hello in Spanish.", ["Hola"]),
]
ORDER_QUESTIONS = ["Where is my order A-1001?", "Track order number 1001 please.", "Where is my order 1002?"]


def tool(name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
    """One "tools" entry, by hand (part 1 shape). Every property is required.

    Args:
        name: e.g. "today".
        description: e.g. "Today's date, e.g. 2026-11-13.".
        properties: e.g. {"order_id": {"type": "string"}}.
    Returns:
        {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}.
    """
    parameters = {"type": "object", "properties": properties, "required": list(properties)}  # = the keys
    return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}


MULTIPLY = tool("multiply", "Multiply two numbers exactly, e.g. 4821 * 3967.",
                {"a": {"type": "number"}, "b": {"type": "number"}})
TODAY = tool("today", "Today's date, e.g. 2026-11-13.", {})
ORDER_WAYS = {  # part 2: the same tool, 3 descriptions
    "with example": tool("order_status", "Look up an order by its id, e.g. A-1001.", {"order_id": ORDER_ID}),
    "no example": tool("order_status", "Look up the status of an order.", {"order_id": ORDER_ID}),
    "field described": tool("order_status", "Look up the status of an order.", {"order_id": ORDER_ID_DESCRIBED}),
}


def run_tool(name: str, arguments: dict[str, Any], forgiving: bool) -> str:
    """Run one call; errors come back as text for the model, never raised.

    Args:
        name: e.g. "order_status".
        arguments: e.g. {"order_id": "1001"}.
        forgiving: True = "1001" counts as "A-1001".
    Returns:
        e.g. "waiting for payment" or "error: order_id must look like A-1001, got '1001'".
    """
    if name == "multiply":
        return str(arguments["a"] * arguments["b"])
    if name == "today":
        return date.today().isoformat()  # e.g. "2026-11-13"
    order_id = str(arguments.get("order_id"))  # .get: None if the model left it out
    if forgiving and order_id.isdigit():
        order_id = "A-" + order_id
    if not order_id.startswith("A-"):
        return f"error: order_id must look like A-1001, got {order_id!r}"
    return ORDERS.get(order_id, f"error: no order {order_id}")


def loop(question: str, tools: list[dict[str, Any]], forgiving: bool) -> str:
    """Call tools until the model answers in text (at most 5 rounds); print each call.

    Args:
        question: e.g. "Where is my order A-1001?".
        tools: e.g. [MULTIPLY, ORDER_WAYS["with example"], TODAY].
        forgiving: passed to run_tool().
    Returns:
        The answer text, or "(gave up)" after 5 rounds of calls.
    """
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT},
                                      {"role": "user", "content": question}]
    for _ in range(5):
        body = {"model": MODEL, "messages": messages, "stream": False, "think": False, "tools": tools,
                "options": {"temperature": 0, "seed": 42, "num_predict": 300}}
        response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=300.0)
        response.raise_for_status()
        message = response.json()["message"]
        messages.append(message)  # as is, tool_calls included
        calls: list[dict[str, Any]] = message.get("tool_calls") or []
        if not calls:
            return message["content"]
        for call in calls:
            name = call["function"]["name"]
            result = run_tool(name, call["function"]["arguments"], forgiving)
            print(f"    call {name}({call['function']['arguments']}) -> {result[:45]!r}")
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return "(gave up)"


def run_questions() -> None:
    """Part 1: all 8 QUESTIONS with the 3 tools; print right / 8 and the time."""
    tools = [MULTIPLY, ORDER_WAYS["with example"], TODAY]
    right = 0
    start = time.perf_counter()
    for item in QUESTIONS:
        print(f"  {item[0]}")
        answer = loop(item[0], tools, False)
        mark = "ok "
        for word in item[1]:
            if word not in answer.replace(",", ""):  # "19,124,907" counts too
                mark = "BAD"
        if mark == "ok ":
            right += 1
        print(f"    {mark} {answer.strip()[:100]!r}")
    print(f"1. loop: right {right}/8, {time.perf_counter() - start:.1f} s\n")


def run_order_ways(way: str, forgiving: bool) -> None:
    """Parts 2 + 3: the 3 order questions with one description of the order tool.

    Args:
        way: a key of ORDER_WAYS, e.g. "no example".
        forgiving: passed to run_tool().
    """
    print(f"{way}, forgiving={forgiving}:")
    for question in ORDER_QUESTIONS:
        answer = loop(question, [MULTIPLY, ORDER_WAYS[way], TODAY], forgiving)
        print(f"  {question:<32} {answer.strip()[:80]!r}")
    print()


if __name__ == "__main__":  # Java: public static void main
    loop("hi", [], False)  # load the model first
    run_questions()
    for way in ORDER_WAYS:
        run_order_ways(way, False)
    run_order_ways("with example", True)
