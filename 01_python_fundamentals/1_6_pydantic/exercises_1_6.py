"""Tests for models_1_6.py: 19 tests, no Ollama. They are the spec.

  uv run pytest 01_python_fundamentals/1_6_pydantic/exercises_1_6.py -v
"""

import pytest
from pydantic import ValidationError

from models_1_6 import Ticket, count_labels, error_fields, parse_ticket

GOOD = '{"text": "Charged twice.", "label": "billing", "priority": 4}'


# ---------- Ticket ----------
def test_ticket_good_and_default_tags() -> None:
    """Valid JSON -> all fields typed; tags defaults to []."""
    ticket = Ticket.model_validate_json(GOOD)
    assert ticket.model_dump() == {"text": "Charged twice.", "label": "billing", "priority": 4, "tags": []}


@pytest.mark.parametrize(("raw_label", "expected"), [(" Billing.", "billing"), ("**BUG**", "bug")])
def test_ticket_cleans_label(raw_label: str, expected: str) -> None:
    """The label is cleaned BEFORE the Literal check.

    Args:
        raw_label: as a model might write it.
        expected: the clean label.
    """
    ticket = Ticket.model_validate({"text": "x", "label": raw_label, "priority": 1})
    assert ticket.model_dump()["label"] == expected


def test_ticket_lax_priority_and_tags() -> None:
    """Lax mode (default): "3" becomes 3. Tags are kept."""
    ticket = Ticket.model_validate({"text": "x", "label": "bug", "priority": "3", "tags": ["web"]})
    assert ticket.model_dump() == {"text": "x", "label": "bug", "priority": 3, "tags": ["web"]}


@pytest.mark.parametrize("data", [
    {"text": "", "label": "bug", "priority": 2},  # empty text
    {"text": "x", "label": "refund", "priority": 2},  # not a label
    {"text": "x", "label": "bug", "priority": 0},  # under 1
    {"text": "x", "label": "bug", "priority": 6},  # over 5
    {"text": "x", "label": "bug", "priority": 2, "team": "web"},  # unknown key
    {"label": "bug", "priority": 2},  # text missing
])
def test_ticket_rejects(data: dict[str, object]) -> None:
    """Each breaks one rule -> ValidationError.

    Args:
        data: a ticket dict with one problem.
    """
    with pytest.raises(ValidationError):
        Ticket.model_validate(data)


# ---------- parse_ticket ----------
def test_parse_ticket_good() -> None:
    """Valid JSON -> a Ticket."""
    ticket = parse_ticket(GOOD)
    assert isinstance(ticket, Ticket)
    assert ticket.model_dump()["priority"] == 4


@pytest.mark.parametrize("json_text", ['{"text": "x", "label": "refund", "priority": 2}', '{"text": '])
def test_parse_ticket_bad(json_text: str) -> None:
    """A broken rule or broken JSON -> None, no exception.

    Args:
        json_text: invalid input.
    """
    assert parse_ticket(json_text) is None


# ---------- error_fields ----------
@pytest.mark.parametrize(("json_text", "expected"), [
    (GOOD, []),
    ('{"text": "", "label": "refund", "priority": 9}', ["text", "label", "priority"]),
    ('{"text": "x", "label": "bug", "priority": 2, "tags": ["web", 5]}', ["tags.1"]),
    ('{"text": ', ["(input)"]),
])
def test_error_fields(json_text: str, expected: list[str]) -> None:
    """Each problem's loc, joined with "."; () -> "(input)".

    Args:
        json_text: the input.
        expected: the paths, in pydantic's order.
    """
    assert error_fields(json_text) == expected


# ---------- count_labels ----------
def test_count_labels() -> None:
    """2 billing, 1 bug, 2 invalid (a bad label + not JSON)."""
    replies = [GOOD, GOOD, '{"text": "Crash.", "label": "Bug.", "priority": 5}',
               '{"text": "x", "label": "refund", "priority": 1}', "Sure! Here is the JSON:"]
    assert count_labels(replies) == {"invalid": 2, "billing": 2, "bug": 1}


def test_count_labels_empty() -> None:
    """No replies -> only the invalid counter, at 0."""
    assert count_labels([]) == {"invalid": 0}
