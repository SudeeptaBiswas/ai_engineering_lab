"""Part 1 of 2: ask for JSON 5 ways, same 8 tickets. Needs Ollama + qwen3:1.7b.

Run (~2.5 min):
  uv run python 03_prompting_tools/3_2_structured_output/examples_3_2_1_formats.py

Goal: the model fills a Triage object (label, priority, summary) that code
can use. Each reply is checked with pydantic (1.6). Two knobs:
  - the system prompt: vague / one example / every field described
  - Ollama's "format": none, or a JSON schema made from the pydantic model
"""

import json  # json.dumps(dict) -> text (1.7)
import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()
from typing import Any, Literal  # Any = "any type". Java: Object

import httpx  # HTTP client (1.7)
from pydantic import BaseModel, ConfigDict, Field, ValidationError

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"

VAGUE_PROMPT = "You triage support tickets. Reply in JSON."
EXAMPLE_PROMPT = ("You triage support tickets. Reply with JSON only, like "
                  '{"label": "bug", "priority": 3, "summary": "Export button crashes app"}. '
                  "label: billing, login, bug or other. priority: 1 (low) to 5 (urgent). "
                  "summary: at most 60 characters.")
FIELDS_PROMPT = ("You triage support tickets. Reply with JSON only, with 3 keys: "
                 "label (one of: billing, login, bug, other), "
                 "priority (1 = low to 5 = urgent; money lost or locked out = 4 or 5), "
                 "summary (at most 60 characters).")

# Same 8 tickets as 3.1: (text, right label)
TICKETS = [
    ("I was charged twice for my subscription this month.", "billing"),
    ("The app crashes when I tap the export button.", "bug"),
    ("I forgot my password and the reset email never arrives.", "login"),
    ("Can you add a dark mode?", "other"),
    ("My card was declined but the money left my account.", "billing"),
    ("After the update, the save button does nothing.", "bug"),
    ("My account is locked after three wrong tries.", "login"),
    ("Where is your office located?", "other"),
]


class Triage(BaseModel):
    """What the model must send back. Same rules style as the 1.6 Ticket."""

    model_config = ConfigDict(extra="forbid")  # unknown keys = error
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)  # 1..5
    summary: str = Field(min_length=1, max_length=60)


def ask(system_prompt: str, ticket: str, schema: dict[str, Any] | None) -> str:
    """One POST /api/chat at temperature 0; the reply text.

    Args:
        system_prompt: e.g. FIELDS_PROMPT.
        ticket: e.g. "Can you add a dark mode?".
        schema: e.g. Triage.model_json_schema(). None = no "format" key.
    Returns:
        The model's reply, e.g. '{"label": "other", "priority": 3, "summary": "Add dark mode"}'.
    """
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": ticket}]
    options = {"temperature": 0, "seed": 42, "num_predict": 200}
    body: dict[str, Any] = {"model": MODEL, "messages": messages, "stream": False,
                            "think": False, "options": options}
    if schema is not None:
        body["format"] = schema  # Ollama only lets the model write tokens that fit it
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=300.0)
    response.raise_for_status()  # 404 = model not pulled
    return response.json()["message"]["content"]


def run(name: str, system_prompt: str, schema: dict[str, Any] | None) -> None:
    """Send all 8 tickets one way; print each reply + valid / right counts and time.

    Args:
        name: e.g. "3. one example + schema".
        system_prompt: e.g. VAGUE_PROMPT.
        schema: passed to ask().
    """
    valid = 0  # replies pydantic accepted
    right = 0  # ... and with the right label
    start = time.perf_counter()
    for ticket in TICKETS:
        text = ticket[0]
        expected_label = ticket[1]
        # --- explicit end ---
        # concise: for text, expected_label in TICKETS:
        answer = ask(system_prompt, text, schema)
        try:
            triage = Triage.model_validate_json(answer)  # JSON text -> checked object (1.6)
            valid += 1
            if triage.label == expected_label:
                right += 1
            note = f"ok, {triage.label}"
        except ValidationError as error:
            note = f"BAD {error.errors()[0]['type']}"  # first problem only, e.g. json_invalid
        # :<8 = pad to 8, left-aligned. !r = with quotes, so "\n" shows
        print(f"  want {expected_label:<8} {note:<16} {answer.strip()[:70]!r}")
    seconds = time.perf_counter() - start
    print(f"{name}: valid {valid}/8, right {right}/8, {seconds:.1f} s\n")


if __name__ == "__main__":  # Java: public static void main
    schema = Triage.model_json_schema()  # the pydantic rules as a JSON Schema dict
    print("The schema Ollama gets:")
    print(json.dumps(schema, indent=1)[:400] + " ...\n")
    ask(VAGUE_PROMPT, "hi", None)  # load the model first, so timings are fair
    run("1. vague prompt", VAGUE_PROMPT, None)
    run("2. vague prompt + schema", VAGUE_PROMPT, schema)
    run("3. one example + schema", EXAMPLE_PROMPT, schema)
    run("4. fields described", FIELDS_PROMPT, None)
    run("5. fields described + schema", FIELDS_PROMPT, schema)
