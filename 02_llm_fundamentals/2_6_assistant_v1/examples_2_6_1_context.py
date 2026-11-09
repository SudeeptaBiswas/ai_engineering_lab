"""Part 1 of 2: why a chatbot needs a memory budget. Needs Ollama + qwen3:1.7b.

Run:
  uv run python 02_llm_fundamentals/2_6_assistant_v1/examples_2_6_1_context.py

Two facts, both measured live:
  1. The history you resend grows every turn (lesson 2.3: no memory).
  2. Past num_ctx, Ollama drops old messages SILENTLY. No error.
"""

import math  # math.ceil = round up. Java: Math.ceil

import httpx  # HTTP client (lesson 1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"  # think=False works on this one (lesson 2.3)

Message = dict[str, str]  # {"role": ..., "content": ...}; a TypedDict in part 2


def chat(messages: list[Message], options: dict[str, int]) -> dict[str, object]:
    """One POST /api/chat, whole reply at once (stream False).

    Args:
        messages: e.g. [{"role": "user", "content": "hi"}].
        options: e.g. {"num_predict": 60, "num_ctx": 1024}.
    Returns:
        The reply JSON; "prompt_eval_count" = tokens the model really read.
    """
    body = {"model": MODEL, "messages": messages, "stream": False,
            "think": False, "options": options}
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=300.0)
    response.raise_for_status()  # 404 = model not pulled
    return response.json()


def estimate_tokens(messages: list[Message]) -> int:
    """Rough token count, the lesson 2.1 way: ~4 characters = 1 token.

    Args:
        messages: e.g. [{"role": "user", "content": "What is RAG?"}] (12 chars).
    Returns:
        e.g. 3. Real counts are higher: roles and markers cost tokens too.
    """
    total = 0
    for message in messages:
        total += math.ceil(len(message["content"]) / 4)
    return total


def answer_text(reply: dict[str, object]) -> str:
    """The answer inside a reply: reply["message"]["content"].

    Args:
        reply: what chat() returned.
    Returns:
        e.g. "Green."
    """
    message = reply["message"]
    assert isinstance(message, dict)  # tells pyright the type; Java: a cast
    return str(message["content"])  # pyright: ignore[reportUnknownArgumentType]


def show_growth() -> None:
    """Fact 1: 4 turns, history resent each time; print real vs estimated tokens."""
    history: list[Message] = [{"role": "system", "content": "Answer in one short sentence."}]
    questions = ["My favourite colour is green.", "What is RAG?",
                 "Name one fruit.", "What is my favourite colour? One word."]
    for question in questions:
        history.append({"role": "user", "content": question})
        reply = chat(history, {"num_predict": 60})
        print(f"  read {reply['prompt_eval_count']:>4} tokens (estimate "
              f"{estimate_tokens(history):>3})  {question!r} -> {answer_text(reply)!r}")
        # The answer goes into the history too, or the next turn forgets it.
        history.append({"role": "assistant", "content": answer_text(reply)})


def show_silent_cut() -> None:
    """Fact 2: same long chat, 2 context sizes. Too small = fact lost, no error."""
    filler_lines: list[str] = []
    for line_number in range(120):  # ~1600 tokens of noise between fact and question
        filler_lines.append(f"Line {line_number}: the weather today is mild and calm.")
    long_chat: list[Message] = [
        {"role": "system", "content": "Answer with one word."},
        {"role": "user", "content": "My favourite colour is green. " + " ".join(filler_lines)},
        {"role": "user", "content": "What is my favourite colour? One word."},
    ]
    print(f"  estimate: {estimate_tokens(long_chat)} tokens")
    for context_size in [4096, 1024]:
        reply = chat(long_chat, {"num_predict": 10, "num_ctx": context_size})
        print(f"  num_ctx {context_size:>4}: read {reply['prompt_eval_count']:>4} tokens"
              f" -> {answer_text(reply)!r}")


# Runs only when started directly, not when pytest imports the file.
if __name__ == "__main__":  # Java: public static void main
    print("1. History grows every turn:")
    show_growth()
    print("2. Over num_ctx, old messages vanish (no error):")
    show_silent_cut()
