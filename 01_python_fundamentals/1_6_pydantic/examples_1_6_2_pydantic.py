"""Part 2 of 2: pydantic checks the data when the code RUNS, from your hints.

Run (instant, no Ollama):
  uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_2_pydantic.py

A pydantic model = a class whose hints are rules. Build one from a dict
or JSON text: every field is checked, bad data raises ValidationError
with ALL problems listed. Java twin: a record + Jackson + Bean Validation
(@NotBlank, @Min, @Max), in one class.
"""

import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class Ticket(BaseModel):
    """A support ticket. Each line below is a type AND a rule."""

    model_config = ConfigDict(extra="forbid")  # unknown keys = error (default: ignored)

    text: str = Field(min_length=1)  # Java: @NotBlank (roughly)
    label: Literal["billing", "login", "bug", "other"]  # only these 4
    priority: int = Field(ge=1, le=5)  # ge = >=, le = <=. Java: @Min(1) @Max(5)
    tags: list[str] = []  # default. Safe here: pydantic copies it (not like a def, 1.3)

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


class StrictTicket(Ticket):
    """Same rules, but priority must be a real JSON number: no "3", no true."""

    priority: int = Field(ge=1, le=5, strict=True)


def show_errors(json_text: str) -> None:
    """Validate one JSON text; print the ticket, or every problem found.

    Args:
        json_text: e.g. '{"text": "", "label": "refund", "priority": 9}'.
    """
    try:
        ticket = Ticket.model_validate_json(json_text)  # Java: mapper.readValue + validate
        print(f"   ok: {ticket!r}")
    except ValidationError as error:
        print(f"   {error.error_count()} problem(s):")
        for problem in error.errors():  # one dict per problem
            field_path = problem["loc"]  # e.g. ("priority",); () = the whole input
            print(f"     {field_path} {problem['type']}: {problem['msg']}")


def main() -> None:
    """Walk through: good data, bad data, lax vs strict, speed."""
    print("1. Good JSON -> a Ticket object, fields typed:")
    ticket = Ticket.model_validate_json('{"text": "Charged twice.", "label": " Billing.", "priority": 4}')
    print(f"   {ticket!r}")
    print(f"   ticket.priority + 1 = {ticket.priority + 1}  (an int, not text)")
    print(f"   back to JSON: {ticket.model_dump_json()}")  # model_dump() = back to a dict

    print("2. Bad JSON -> ValidationError, every problem at once:")
    show_errors('{"text": "", "label": "refund", "priority": 9}')
    show_errors('{"label": "bug"}')
    show_errors('{"text": "x", "label": "bug", "priority": 2, "team": "web"}')
    show_errors('{"text": ')  # not even JSON

    print('3. Lax by default: "3" and true become ints. Strict refuses:')
    for json_text in ['{"text": "x", "label": "bug", "priority": "3"}',
                      '{"text": "x", "label": "bug", "priority": true}']:
        lax = Ticket.model_validate_json(json_text)
        try:
            StrictTicket.model_validate_json(json_text)
            strict_result = "ok"
        except ValidationError as error:
            strict_result = error.errors()[0]["type"]
        print(f"   {json_text}\n     lax: priority={lax.priority!r}   strict: {strict_result}")

    print("4. Speed: 10 000 validations")
    start = time.perf_counter()
    for _ in range(10_000):
        Ticket.model_validate_json('{"text": "x", "label": "bug", "priority": 2}')
    seconds = time.perf_counter() - start
    print(f"   {seconds:.3f} s total, {seconds / 10_000 * 1_000_000:.1f} microseconds each")


if __name__ == "__main__":  # Java: public static void main
    main()
