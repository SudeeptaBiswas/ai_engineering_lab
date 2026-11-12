"""Lesson 1.6 exercises: a pydantic Ticket model + 3 functions. YOU fill them.

Write the Ticket fields, then replace each `raise NotImplementedError`,
until every test in exercises_1_6.py passes:
  uv run pytest 01_python_fundamentals/1_6_pydantic/exercises_1_6.py -v
No Ollama needed. Look at examples_1_6_2_pydantic.py for the syntax.
"""
from typing import Literal, get_args
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

Label = Literal["billing", "login", "bug", "other"]  # the one source of labels
LABELS: list[str] = list(get_args(Label))  # built from Label, never typed twice



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
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    label: Label
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []

    @field_validator("label", mode="before")  # runs BEFORE the Literal check
    @classmethod  # gets the class, not an object. Java: static
    def clean_label(cls, value: object) -> object:
        """Tidy the label first: " Billing." -> "billing" (the 3.1 cleaning).

        Args:
            value: the raw input for "label", any type.
        Returns:
            The cleaned text, or value unchanged if it is not text.
        """
        if isinstance(value, str):
            return value.strip().lower().strip(".*")
        return value


def parse_ticket(json_text: str) -> Ticket | None:
    """JSON text -> Ticket, or None if it is broken or breaks a rule.

    Args:
        json_text: e.g. '{"text": "Charged twice.", "label": "billing", "priority": 4}'.
    Returns:
        The Ticket. None for any ValidationError (bad JSON is one too).
    """
    try:
        return Ticket.model_validate_json(json_text)
    except ValidationError:
        return None



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
    try:
        Ticket.model_validate_json(json_text)
        return []
    except ValidationError as error:
        fields: list[str] = []
        for problem in error.errors():  # one dict per problem
            loc = problem["loc"]  # Define loc here
            if not loc:
                fields.append("(input)")
            else: 
                fields.append(".".join(str(part) for part in loc))  # e.g. ("priority",); () = the whole input
        return fields


def count_labels(json_texts: list[str]) -> dict[str, int]:
    """Count tickets per label; tickets that fail parse_ticket count as "invalid".

    Args:
        json_texts: e.g. 3 model replies, one of them broken.
    Returns:
        e.g. {"invalid": 1, "billing": 2}. "invalid" is always there (0 if none).
        Labels with no tickets are left out.
    """
    counts = {"invalid": 0}

    for json_text in json_texts:
        ticket = parse_ticket(json_text)

        if ticket is None:
            counts["invalid"] += 1
        else:
            counts[ticket.label] = counts.get(ticket.label, 0) + 1

    return counts
