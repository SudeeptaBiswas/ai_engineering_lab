"""Lesson 3.1 exercises: prompt patterns as small functions. YOU fill them.

Replace each `raise NotImplementedError` with code, until every test in
exercises_3_1.py passes:
  uv run pytest 03_prompting_tools/3_1_prompt_patterns/exercises_3_1.py -v
Ollama off? Add -m "not ollama".
"""

from typing import Any  # "any type". Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until classify() uses it

from assistant.memory import Message  # {"role": ..., "content": ...} (2.6)

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows (1.7)
MODEL = "qwen3:1.7b"
LABELS = ["billing", "login", "bug", "other"]
SYSTEM_PROMPT = "You sort support tickets. Reply with exactly one word: billing, login, bug, or other."
# Few-shot examples: (ticket, label). Shown to the model as past chat turns.
EXAMPLES = [
    ("I need a copy of last month's invoice.", "billing"),
    ("The two-factor code is never accepted.", "login"),
    ("Images do not load on the settings page.", "bug"),
    ("Do you have a student discount?", "other"),
]


def few_shot_messages(system_prompt: str, examples: list[tuple[str, str]], question: str) -> list[Message]:
    """Build a few-shot chat: rules, then examples as fake turns, then the question.

    Each example becomes 2 messages: a "user" one (the input) and an
    "assistant" one (the right output), as if the model had answered before.
    Args:
        system_prompt: e.g. SYSTEM_PROMPT.
        examples: e.g. [("Do you have a student discount?", "other")]. [] = no shots.
        question: e.g. "Can you add a dark mode?".
    Returns:
        [system, user, assistant, ..., user(question)]. 1 + 2 * len(examples) + 1 messages.
    """
    raise NotImplementedError


def parse_label(answer: str, labels: list[str]) -> str | None:
    """Turn a model answer into one of the labels, or None if it isn't one.

    Clean first: strip spaces/newlines, lower case, then strip "." and "*"
    from both ends (the model writes "Billing." or "**bug**").
    Args:
        answer: e.g. " Billing.\n".
        labels: e.g. LABELS.
    Returns:
        e.g. "billing". None for "This is a bug." (a sentence is NOT a label).
    """
    raise NotImplementedError


def final_answer(text: str) -> str | None:
    """The text after "Answer:" on the LAST line that starts with it.

    Case does not matter ("answer: 8" counts). Hint: text.splitlines(),
    line.strip().lower().startswith("answer:"), line.split(":", 1)[1].
    Args:
        text: e.g. "Step 1: 23 - 9 = 14\\nAnswer: 50".
    Returns:
        e.g. "50" (stripped). None if no line starts with "Answer:".
    """
    raise NotImplementedError


def same_number(got: str | None, expected: str) -> bool:
    """True if got and expected are the same number: "8.00" vs "8" -> True.

    Args:
        got: e.g. final_answer(...) output: "8.00", "eight" or None.
        expected: e.g. "8".
    Returns:
        False for None or text that is not a number (catch ValueError, 1.5).
    """
    raise NotImplementedError


def score(predictions: list[Any], expected: list[Any]) -> float:
    """Share of predictions equal to the expected value at the same index.

    Args:
        predictions: e.g. ["billing", "bug"].
        expected: e.g. ["billing", "login"].
    Returns:
        e.g. 0.5. Both empty -> 0.0.
    Raises:
        ValueError: different lengths (a silent zip() would hide a bug, 2.5).
    """
    raise NotImplementedError


def classify(ticket: str) -> str | None:
    """Ask the model for the ticket's label, few-shot, and parse the reply.

    POST {OLLAMA_URL}/api/chat, timeout 120, JSON body:
      {"model": MODEL, "messages": few_shot_messages(SYSTEM_PROMPT, EXAMPLES, ticket),
       "stream": False, "think": False,
       "options": {"temperature": 0, "seed": 42, "num_predict": 20}}
    raise_for_status(), then parse_label(reply["message"]["content"], LABELS).
    Args:
        ticket: e.g. "I was charged twice for my subscription this month.".
    Returns:
        e.g. "billing". None if the model's reply is not a label.
    Raises:
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
    """
    raise NotImplementedError
