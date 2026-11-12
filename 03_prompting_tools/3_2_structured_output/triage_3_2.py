"""Lesson 3.2 exercises: JSON triage with a schema, checks and retries. YOU fill them.

Replace each `raise NotImplementedError` with code, until every test in
this folder passes (exercises_3_2_1_parse.py first, then _2_triage.py):
  uv run pytest 03_prompting_tools/3_2_structured_output -v
Ollama off? Add -m "not ollama".
"""

from typing import Any, Literal  # Any = "any type". Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until triage() uses it
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from assistant.memory import Message  # {"role": ..., "content": ...} (2.6)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
# Every field described, no example values (part 1: an example got copied, 2/8 right).
SYSTEM_PROMPT = ("You triage support tickets. Reply with JSON only, with 3 keys: "
                 "label (one of: billing, login, bug, other), "
                 "priority (1 = low to 5 = urgent; money lost or locked out = 4 or 5), "
                 "summary (at most 60 characters).")


class Triage(BaseModel):
    """What the model must send back. Given: you wrote one like it in 1.6."""

    model_config = ConfigDict(extra="forbid")
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=60)


def cut_out_json(text: str) -> str:
    """From the first "{" to the last "}", to drop ```json fences and chatter.

    Hint: text.find("{"), text.rfind("}"), slicing (1.3).
    Args:
        text: e.g. 'Sure!\\n```json\\n{"label": "bug"}\\n```'.
    Returns:
        e.g. '{"label": "bug"}'. The text unchanged if there is no "{" ... "}".
    """
    raise NotImplementedError


def chat_body(messages: list[Message], schema: dict[str, Any] | None) -> dict[str, Any]:
    """The JSON body for POST /api/chat.

    Always: model, messages, "stream": False, "think": False,
    "options": {"temperature": 0, "seed": 42, "num_predict": 200}.
    Only if schema is not None: "format": schema.
    Args:
        messages: e.g. [system, user].
        schema: e.g. Triage.model_json_schema(), or None.
    Returns:
        The body dict, ready for httpx.post(..., json=body).
    """
    raise NotImplementedError


def feedback(error: ValidationError) -> str:
    """The user message for a retry: every problem on its own line.

    First line "Your JSON broke these rules:", then one line per problem
    "- <where>: <msg>" (where = loc joined by ".", or "(input)" if loc is
    empty, as in 1.6 error_fields), last line "Reply with the fixed JSON only.".
    Args:
        error: e.g. from Triage.model_validate_json('{"label": "refund", ...}').
    Returns:
        e.g. "Your JSON broke these rules:\\n- label: Input should be ...\\nReply with the fixed JSON only."
    """
    raise NotImplementedError


def triage(ticket: str, max_tries: int = 3) -> Triage | None:
    """Ask for a Triage with the schema; on a ValidationError, feed it back and retry.

    messages = [system SYSTEM_PROMPT, user ticket]. Each try:
      POST {OLLAMA_URL}/api/chat, json=chat_body(messages, Triage.model_json_schema()),
      timeout 300, raise_for_status(), answer = reply["message"]["content"].
      Triage.model_validate_json(cut_out_json(answer)) -> return it.
      ValidationError -> append {"role": "assistant", "content": answer}
      and {"role": "user", "content": feedback(error)}, then try again.
    Args:
        ticket: e.g. "Can you add a dark mode?".
        max_tries: most POSTs, e.g. 3.
    Returns:
        The Triage. None if every try failed.
    Raises:
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
    """
    raise NotImplementedError
