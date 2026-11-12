"""Lesson 1.6 exercises: a pydantic Ticket model + 3 functions. YOU fill them.

Write the Ticket fields, then replace each `raise NotImplementedError`,
until every test in exercises_1_6.py passes:
  uv run pytest 01_python_fundamentals/1_6_pydantic/exercises_1_6.py -v
No Ollama needed. Look at examples_1_6_2_pydantic.py for the syntax.
"""

from pydantic import BaseModel, ValidationError  # pyright: ignore[reportUnusedImport] — until you use it

LABELS = ["billing", "login", "bug", "other"]


class Ticket(BaseModel):
    """A support ticket, as a model might return it in JSON (3.2).

    Fields to write (the tests check each rule):
      text: str, at least 1 character
      label: one of LABELS exactly. Before the check, clean it:
             " Billing." -> "billing", "**BUG**" -> "bug" (strip, lower, strip ".*")
      priority: int from 1 to 5
      tags: list of str, default [] (empty)
    Unknown keys (e.g. "team") must be an error, not silently dropped.
    Hints: Field(...), Literal[...], ConfigDict(extra=...), @field_validator.
    """

    pass  # TODO: delete this line, write the fields


def parse_ticket(json_text: str) -> Ticket | None:
    """JSON text -> Ticket, or None if it is broken or breaks a rule.

    Args:
        json_text: e.g. '{"text": "Charged twice.", "label": "billing", "priority": 4}'.
    Returns:
        The Ticket. None for any ValidationError (bad JSON is one too).
    """
    raise NotImplementedError


def error_fields(json_text: str) -> list[str]:
    """Where each problem is, as text, in the order pydantic reports them.

    Each problem's "loc" is a path: ("priority",) or ("tags", 1) = the
    2nd tag. Join its parts with "." -> "priority", "tags.1". An empty
    loc () means the whole input (e.g. not JSON at all) -> "(input)".
    Args:
        json_text: e.g. '{"text": "", "label": "refund", "priority": 2}'.
    Returns:
        e.g. ["text", "label"]. [] if the ticket is valid.
    """
    raise NotImplementedError


def count_labels(json_texts: list[str]) -> dict[str, int]:
    """Count tickets per label; tickets that fail parse_ticket count as "invalid".

    Args:
        json_texts: e.g. 3 model replies, one of them broken.
    Returns:
        e.g. {"invalid": 1, "billing": 2}. "invalid" is always there (0 if none).
        Labels with no tickets are left out.
    """
    raise NotImplementedError
