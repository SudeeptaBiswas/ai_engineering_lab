"""Part 1 of 2: the same 8 tickets, 3 prompts. Needs Ollama + qwen3:1.7b.

Run (~45 s):
  uv run python 03_prompting_tools/3_1_prompt_patterns/examples_3_1_1_classify.py

Goal: code must read ONE word back (billing / login / bug / other), so a
router can send the ticket to the right team. Which prompt gets that?
  1. zero-shot  : just the question
  2. system     : + rules in a system message (like "Be brief." in 2.6)
  3. few-shot   : + 4 solved examples as past chat turns
"""

import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()
# Callable[[str], list[Message]] = "a function: str in, list out". Java: Function<String, List<Message>>
from collections.abc import Callable

import httpx  # HTTP client (lesson 1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
LABELS = ["billing", "login", "bug", "other"]
SYSTEM_PROMPT = "You sort support tickets. Reply with exactly one word: billing, login, bug, or other."

Message = dict[str, str]  # {"role": ..., "content": ...}

# The 8 tickets to sort, each with the right label (what a human said).
TICKETS = [
    {"text": "I was charged twice for my subscription this month.", "label": "billing"},
    {"text": "The app crashes when I tap the export button.", "label": "bug"},
    {"text": "I forgot my password and the reset email never arrives.", "label": "login"},
    {"text": "Can you add a dark mode?", "label": "other"},
    {"text": "My card was declined but the money left my account.", "label": "billing"},
    {"text": "After the update, the save button does nothing.", "label": "bug"},
    {"text": "My account is locked after three wrong tries.", "label": "login"},
    {"text": "Where is your office located?", "label": "other"},
]
# Solved examples for few-shot. NOT the same tickets as above (that would be cheating).
EXAMPLES = [
    {"text": "I need a copy of last month's invoice.", "label": "billing"},
    {"text": "The two-factor code is never accepted.", "label": "login"},
    {"text": "Images do not load on the settings page.", "label": "bug"},
    {"text": "Do you have a student discount?", "label": "other"},
]


def ask(messages: list[Message]) -> dict[str, object]:
    """One POST /api/chat, whole reply at once, temperature 0 (lesson 2.4).

    Args:
        messages: e.g. [{"role": "user", "content": "Classify: ..."}].
    Returns:
        The reply JSON. ["message"]["content"] = the answer,
        ["prompt_eval_count"] = tokens the model read.
    """
    # temperature 0 + a fixed seed = the same answer every run (measured: 2 runs equal)
    options = {"temperature": 0, "seed": 42, "num_predict": 60}
    body = {"model": MODEL, "messages": messages, "stream": False, "think": False, "options": options}
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=120.0)
    response.raise_for_status()  # 404 = model not pulled
    return response.json()


def zero_shot(ticket: str) -> list[Message]:
    """Prompt 1: only the question, no rules.

    Args:
        ticket: e.g. "Can you add a dark mode?".
    Returns:
        1 message.
    """
    return [{"role": "user", "content": f"Classify this support ticket: {ticket}"}]


def with_system(ticket: str) -> list[Message]:
    """Prompt 2: the rules in a system message, then the ticket.

    Args:
        ticket: e.g. "Can you add a dark mode?".
    Returns:
        2 messages: system, user.
    """
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": ticket}]


def few_shot(ticket: str) -> list[Message]:
    """Prompt 3: rules, then each example as a fake user/assistant turn, then the ticket.

    The model reads the examples as "what I answered before" (memory, 2.6)
    and copies the pattern: same format, same idea of each label.
    Args:
        ticket: e.g. "Can you add a dark mode?".
    Returns:
        10 messages: system, 4 x (user, assistant), user.
    """
    messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for example in EXAMPLES:
        messages.append({"role": "user", "content": example["text"]})
        messages.append({"role": "assistant", "content": example["label"]})  # the "right answer"
    messages.append({"role": "user", "content": ticket})
    return messages


def run(name: str, build: Callable[[str], list[Message]]) -> None:
    """Send all 8 tickets with one prompt style; print each answer + the totals.

    Args:
        name: e.g. "few-shot".
        build: one of zero_shot / with_system / few_shot (a function is a value, 1.2).
    """
    in_format = 0  # answers that ARE one of the labels
    correct = 0
    prompt_tokens = 0  # tokens the model read, for the last ticket
    start = time.perf_counter()
    for ticket in TICKETS:
        reply = ask(build(ticket["text"]))
        prompt_tokens = reply["prompt_eval_count"]
        message = reply["message"]
        assert isinstance(message, dict)  # tells pyright the type; Java: a cast
        answer = str(message["content"])  # pyright: ignore[reportUnknownArgumentType]
        cleaned = answer.strip().lower().rstrip(".")  # " Billing." -> "billing"
        if cleaned in LABELS:
            in_format += 1
        if cleaned == ticket["label"]:
            correct += 1
        mark = "ok  "
        if cleaned != ticket["label"]:
            mark = "MISS"
        # [:60] = first 60 characters. !r = with quotes, so "\n" is visible
        print(f"  {mark} {ticket['label']:<8} <- {answer.strip()[:60]!r}")
    seconds = time.perf_counter() - start
    print(f"{name}: one label {in_format}/8, correct {correct}/8, {seconds:.1f} s, "
          f"prompt tokens {prompt_tokens} (last ticket)\n")


if __name__ == "__main__":  # Java: public static void main
    ask([{"role": "user", "content": "hi"}])  # load the model first, so timings are fair
    run("1. zero-shot", zero_shot)
    run("2. system", with_system)
    run("3. few-shot", few_shot)
