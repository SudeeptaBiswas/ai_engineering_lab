"""Part 2 of 2: when the JSON is bad, send the errors back and ask again.

Run (~3 min, needs Ollama + qwen3:1.7b):
  uv run python 03_prompting_tools/3_2_structured_output/examples_3_2_2_retry.py

  1. retry only            : vague prompt, up to 3 tries, errors fed back
  2. + cut out the {...}   : same, but strip ```json fences / extra text first
  3. schema with a limit   : maxLength 30 in the schema -> text cut mid-word
"""

import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()
from typing import Any, Literal  # Any = "any type". Java: Object

import httpx  # HTTP client (1.7)
from pydantic import BaseModel, ConfigDict, Field, ValidationError

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
KEYS_PROMPT = "You triage support tickets. Reply in JSON with label, priority and summary."
WORDS_PROMPT = ("You triage support tickets. Reply with JSON: label (billing, login, bug, other), "
                "priority (1-5), summary (a full sentence that repeats the customer's words).")
TICKETS = [  # same 8 as part 1: (text, right label)
    ("I was charged twice for my subscription this month.", "billing"),
    ("The app crashes when I tap the export button.", "bug"),
    ("I forgot my password and the reset email never arrives.", "login"),
    ("Can you add a dark mode?", "other"),
    ("My card was declined but the money left my account.", "billing"),
    ("After the update, the save button does nothing.", "bug"),
    ("My account is locked after three wrong tries.", "login"),
    ("Where is your office located?", "other"),
]
Message = dict[str, str]  # {"role": ..., "content": ...}


class Triage(BaseModel):
    """Same model as part 1."""

    model_config = ConfigDict(extra="forbid")
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=60)


class ShortTriage(Triage):
    """Summary at most 30 characters: a limit the model can't count well."""

    summary: str = Field(min_length=1, max_length=30)


def ask(messages: list[Message], schema: dict[str, Any] | None) -> str:
    """One POST /api/chat at temperature 0; the reply text.

    Args:
        messages: e.g. [system, user] or, on a retry, [system, user, assistant, user].
        schema: a JSON Schema for "format", or None.
    Returns:
        The model's reply text.
    """
    body: dict[str, Any] = {"model": MODEL, "messages": messages, "stream": False, "think": False,
                            "options": {"temperature": 0, "seed": 42, "num_predict": 200}}
    if schema is not None:
        body["format"] = schema
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=300.0)
    response.raise_for_status()
    return response.json()["message"]["content"]


def cut_out_json(text: str) -> str:
    """From the first "{" to the last "}": drops ```json fences and chatter.

    Args:
        text: e.g. '```json\\n{"label": "bug"}\\n```'.
    Returns:
        e.g. '{"label": "bug"}'. The text unchanged if it has no {...}.
    """
    start = text.find("{")  # -1 if missing. Java: indexOf
    end = text.rfind("}")  # last one. Java: lastIndexOf
    if start == -1 or end < start:
        return text
    return text[start:end + 1]  # +1: the end index is not included (1.3 slicing)


def feedback(error: ValidationError) -> str:
    """The next user message: every problem, one line each, then "fix it".

    Args:
        error: from Triage.model_validate_json(...).
    Returns:
        e.g. "Your JSON broke these rules:\\n- priority: Input should be a valid integer...".
    """
    lines = ["Your JSON broke these rules:"]
    for problem in error.errors():
        where = ".".join(str(part) for part in problem["loc"]) or "(input)"  # rule-ok: 1.6 error_fields
        lines.append(f"- {where}: {problem['msg']}")
    lines.append("Reply with the fixed JSON only.")
    return "\n".join(lines)


def run(name: str, cut: bool, tries: int) -> None:
    """Triage all 8 tickets with retries; print each try + the totals.

    Args:
        name: e.g. "2. + cut out the {...}".
        cut: True = cut_out_json() before validating.
        tries: most calls per ticket, e.g. 3.
    """
    valid_on_try = [0] * tries  # [0, 0, 0]: tickets that became valid on try 1, 2, 3
    right = 0
    calls = 0
    start = time.perf_counter()
    for text, expected_label in TICKETS:  # rule-ok: tuple unpacking (1.2), part 1 shows the long form
        messages: list[Message] = [{"role": "system", "content": KEYS_PROMPT},
                                   {"role": "user", "content": text}]
        for attempt in range(tries):  # 0, 1, 2
            answer = ask(messages, None)
            calls += 1
            json_text = answer
            if cut:
                json_text = cut_out_json(answer)
            try:
                triage = Triage.model_validate_json(json_text)
                valid_on_try[attempt] += 1
                if triage.label == expected_label:
                    right += 1
                print(f"  try {attempt + 1} ok   want {expected_label:<8} got {triage.model_dump()}")
                break  # valid: stop retrying
            except ValidationError as error:
                print(f"  try {attempt + 1} BAD  {answer.strip()[:60]!r}")
                messages.append({"role": "assistant", "content": answer})  # what it said
                messages.append({"role": "user", "content": feedback(error)})  # what was wrong
    print(f"{name}: valid on try 1/2/3 = {valid_on_try}, right {right}/8, "
          f"{calls} calls, {time.perf_counter() - start:.1f} s\n")


def schema_cuts() -> None:
    """maxLength 30 sent in the schema: Ollama stops the text at 30 characters."""
    schema = ShortTriage.model_json_schema()  # has "maxLength": 30
    for ticket in TICKETS:
        messages: list[Message] = [{"role": "system", "content": WORDS_PROMPT},
                                   {"role": "user", "content": ticket[0]}]  # [0] = the text
        triage = ShortTriage.model_validate_json(ask(messages, schema))  # never fails here
        print(f"  {len(triage.summary):>2} chars {triage.summary!r}")
    print("3. schema with a limit: all valid, some cut mid-word or garbled\n")


if __name__ == "__main__":  # Java: public static void main
    ask([{"role": "user", "content": "hi"}], None)  # load the model first
    run("1. retry only", False, 3)
    run("2. + cut out the {...}", True, 3)
    schema_cuts()
