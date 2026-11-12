"""Tests for triage_3_2.py, part 1: cut_out_json, chat_body, feedback (10, no Ollama).

  uv run pytest 03_prompting_tools/3_2_structured_output/exercises_3_2_1_parse.py -v
"""

import pytest
from pydantic import ValidationError

from assistant.memory import Message
from triage_3_2 import Triage, chat_body, cut_out_json, feedback

GOOD = '{"label": "other", "priority": 2, "summary": "Add dark mode"}'


# ---------- cut_out_json ----------
@pytest.mark.parametrize(("text", "expected"), [
    (GOOD, GOOD),
    ('```json\n{"label": "bug"}\n```', '{"label": "bug"}'),  # fences (measured, part 2)
    ('Sure! {"a": {"b": 1}} Hope that helps.', '{"a": {"b": 1}}'),  # nested: LAST "}"
    ("I can't help with that.", "I can't help with that."),  # no braces: unchanged
    ("} oops {", "} oops {"),  # "}" before "{": unchanged
])
def test_cut_out_json(text: str, expected: str) -> None:
    """First "{" to last "}", else the text as it was.

    Args:
        text: a model reply.
        expected: what cut_out_json must return.
    """
    assert cut_out_json(text) == expected


# ---------- chat_body ----------
def test_chat_body_with_schema() -> None:
    """A schema goes in under "format"."""
    messages: list[Message] = [{"role": "user", "content": "Hi"}]
    assert chat_body(messages, {"type": "object"}) == {
        "model": "qwen3:1.7b", "messages": messages, "stream": False, "think": False,
        "options": {"temperature": 0, "seed": 42, "num_predict": 200},
        "format": {"type": "object"},
    }


def test_chat_body_without_schema() -> None:
    """No schema: no "format" key at all (not "format": None)."""
    assert "format" not in chat_body([], None)


# ---------- feedback ----------
def errors_of(json_text: str) -> ValidationError:
    """The ValidationError that Triage raises for this text.

    Args:
        json_text: bad JSON for Triage.
    Returns:
        The caught error.
    """
    with pytest.raises(ValidationError) as caught:
        Triage.model_validate_json(json_text)
    return caught.value


def test_feedback_lines() -> None:
    """Header, one line per problem (pydantic's order), closing line."""
    error = errors_of('{"label": "Bug Report", "priority": "High", "summary": "x"}')
    lines = feedback(error).splitlines()
    assert lines[0] == "Your JSON broke these rules:"
    assert lines[1].startswith("- label: Input should be 'billing'")
    assert lines[2].startswith("- priority: Input should be a valid integer")
    assert lines[3] == "Reply with the fixed JSON only."
    assert len(lines) == 4


def test_feedback_whole_input() -> None:
    """Not JSON at all: loc is () -> "(input)"."""
    lines = feedback(errors_of("```json\n{")).splitlines()
    assert lines[1].startswith("- (input): Invalid JSON")


def test_feedback_extra_key() -> None:
    """An unknown key is named, so the model knows what to drop."""
    error = errors_of('{"label": "bug", "priority": 2, "summary": "x", "team": "web"}')
    assert feedback(error).splitlines()[1] == "- team: Extra inputs are not permitted"
