"""Part 1 of 2: one tool call by hand, step by step. Needs Ollama + qwen3:1.7b.

Run (~3 min):
  uv run python 03_prompting_tools/3_3_tool_calling/examples_3_3_1_calls.py

  1. with tools   : the model asks US to run multiply(a, b)
  2. send result  : we run it, send the result back, get the answer
  3. two at once  : two tool calls in one reply
  4. no tool fits : a plain answer, no tool call
  5. score        : 5 products, no tools vs tools
"""

import json  # json.dumps(dict) -> text (1.7)
import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()
from typing import Any  # "any type". Java: Object

import httpx  # HTTP client (1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
# A tool, by hand: name + description + a JSON Schema for its arguments (3.2).
MULTIPLY_TOOL = {
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "Multiply two numbers exactly, e.g. 4821 * 3967.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
}
PRODUCTS = [(4821, 3967), (239, 571), (78, 96), (12345, 678), (9876, 5432)]


def chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None) -> dict[str, Any]:
    """One POST /api/chat at temperature 0; the reply's "message" dict.

    Args:
        messages: e.g. [{"role": "user", "content": "What is 4821 * 3967?"}].
        tools: e.g. [MULTIPLY_TOOL], or None = no "tools" key.
    Returns:
        e.g. {"role": "assistant", "content": "", "tool_calls": [...]}.
    """
    body: dict[str, Any] = {"model": MODEL, "messages": messages, "stream": False, "think": False,
                            "options": {"temperature": 0, "seed": 42, "num_predict": 1000}}
    if tools is not None:
        body["tools"] = tools  # the model may now ask for a call instead of answering
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=300.0)
    response.raise_for_status()  # 404 = model not pulled
    return response.json()["message"]


def solve(question: str) -> str:
    """Ask with the tool; run every call it asks for; ask again; the answer text.

    Args:
        question: e.g. "What is 4821 * 3967?".
    Returns:
        e.g. "The result of 4821 x 3967 is 19124907."
    """
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    reply = chat(messages, [MULTIPLY_TOOL])
    messages.append(reply)  # its own reply, with tool_calls: it must see what it asked
    calls: list[dict[str, Any]] = reply.get("tool_calls") or []  # `or []`: None -> empty list
    for call in calls:
        arguments = call["function"]["arguments"]  # already a dict, not JSON text
        result = str(arguments["a"] * arguments["b"])  # WE do the maths, not the model
        print(f"  we ran multiply({arguments}) -> {result}")
        messages.append({"role": "tool", "tool_name": "multiply", "content": result})
    if len(messages) == 2:  # no tool call: the first reply is the answer
        return reply["content"]
    reply2 = chat(messages, [MULTIPLY_TOOL])["content"]
    return reply2


def show(title: str, message: dict[str, Any]) -> None:
    """Print the reply text (end only, if long) and its tool calls as JSON.

    Args:
        title: e.g. "1. with tools".
        message: a reply from chat().
    """
    content = message["content"].strip()
    print(f"{title}\n  content   : {content[-90:]!r}")  # [-90:] = last 90 characters
    print(f"  tool_calls: {json.dumps(message.get('tool_calls'))}\n")  # None -> null


def score(use_tools: bool) -> None:
    """Ask all 5 products; print right / 5 and the time.

    Args:
        use_tools: True = solve() with the tool, False = the model alone.
    """
    right = 0
    start = time.perf_counter()
    for pair in PRODUCTS:
        question = f"What is {pair[0]} * {pair[1]}?"
        if use_tools:
            answer = solve(question)
        else:
            answer = chat([{"role": "user", "content": question}], None)["content"]
        expected = str(pair[0] * pair[1])
        mark = "BAD"
        if expected in answer.replace(",", ""):  # "19,124,907" counts too
            right += 1
            mark = "ok "
        print(f"  {question:<26} want {expected:<9} {mark} {answer.strip()[-40:]!r}")
    print(f"5. tools={use_tools}: right {right}/5, {time.perf_counter() - start:.1f} s\n")


if __name__ == "__main__":  # Java: public static void main
    # question = {"role": "user", "content": "What is 4821 * 3967?"}
    # chat([question], None)  # load the model first, so timings are fair
    #show("========", chat([{"role": "user", "content": "What is 2 * 3 * 4?"}], [MULTIPLY_TOOL]))   
    print(f"  answer: {solve('What is 2 * 3 * 4?')!r}\n")
    # reply = chat([question], [MULTIPLY_TOOL])
    # show("1. with tools", reply)
    # print("2. we run it and send the result back:")
    # print(f"  answer: {solve('What is 4821 * 3967?')!r}\n")
    # show("3. two at once", chat([{"role": "user", "content": "What is 12.5 * 8 and what is 7 * 6?"}],
    #                             [MULTIPLY_TOOL]))
    # show("4. no tool fits", chat([{"role": "user", "content": "What is the capital of France?"}],
    #                              [MULTIPLY_TOOL]))
    score(False)
    score(True)
