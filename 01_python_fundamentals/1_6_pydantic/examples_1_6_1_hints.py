"""Part 1 of 2: type hints are checked by pyright, NOT when the code runs.

Run (instant, no Ollama):
  uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_1_hints.py

Java checks types twice: javac, and the JVM (ClassCastException).
Python checks them zero times by itself. pyright reads your hints before
you run; at run time they are just notes. So data from OUTSIDE your code
(JSON from an API, a model's reply) is never checked. That gap is why
pydantic exists (part 2).
"""

import json
from dataclasses import dataclass
from typing import Literal, TypedDict

# Literal = "only these exact values". Java: an enum. pyright flags Label = "refund".
Label = Literal["billing", "login", "bug", "other"]


class TicketDict(TypedDict):
    """A dict with known keys (2.6). pyright checks it; at run time a plain dict."""

    text: str
    label: Label
    priority: int  # 1 (low) .. 5 (urgent)


@dataclass
class TicketData:
    """A dataclass (1.4): __init__ written for you. It does NOT check types."""

    text: str
    priority: int


def describe(ticket: TicketDict) -> str:
    """One line about a ticket. pyright trusts that ticket["priority"] is an int.

    Args:
        ticket: e.g. {"text": "Charged twice.", "label": "billing", "priority": 4}.
    Returns:
        e.g. "billing, priority 4, urgent: False".
    """
    urgent = False
    try:
        urgent = ticket["priority"] >= 4  # a str here -> TypeError at RUN time
    except TypeError as error:
        return f"{ticket['label']}, CRASH: {error}"
    return f"{ticket['label']}, priority {ticket['priority']}, urgent: {urgent}"


def main() -> None:
    """Show 3 ways wrong data gets past type hints."""
    print("1. Hints are not checked at run time:")
    # pyright flags the next line in the editor; Python runs it anyway.
    wrong = TicketData(text=5, priority="high")  # pyright: ignore[reportArgumentType]
    print(f"   TicketData(text=5, priority='high') -> {wrong}")

    print("2. JSON comes in untyped. json.loads returns Any, so pyright can't help:")
    good_reply = '{"text": "Charged twice.", "label": "billing", "priority": 4}'
    bad_reply = '{"text": "Charged twice.", "label": "refund", "priority": "high"}'
    good_ticket: TicketDict = json.loads(good_reply)  # Any -> TicketDict: no check
    bad_ticket: TicketDict = json.loads(bad_reply)  # pyright says nothing here either
    print(f"   good: {describe(good_ticket)}")
    print(f"   bad:  {describe(bad_ticket)}")
    print("   'refund' is not a Label, but nothing noticed. The crash came later,")
    print("   far from where the bad data came in.")

    print("3. A hand-written check works, but grows with every field:")
    problems: list[str] = []
    # object = "could be anything": the honest type of data from outside. Java: Object
    raw_ticket: dict[str, object] = json.loads(bad_reply)
    priority = raw_ticket["priority"]
    label = raw_ticket["label"]
    if not isinstance(priority, int):  # Java: instanceof
        problems.append("priority is not an int")
    if label not in ("billing", "login", "bug", "other"):
        problems.append("label is not a known label")
    print(f"   {problems}")
    print("   pydantic writes these checks for you, from the hints (part 2).")


if __name__ == "__main__":  # Java: public static void main
    main()
