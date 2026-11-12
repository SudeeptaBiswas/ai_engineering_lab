"""Lesson 3.3: the 3 tools the model may call. GIVEN: read it, don't change it.

Your code is in tool_calls_3_3.py. Each tool = an args model (pydantic,
1.6) + a function that takes the checked args and returns text.
"""

import re  # re.fullmatch = whole text matches a pattern. Java: Pattern.matches
from collections.abc import Callable  # a function type. Java: Function<T, R>
from dataclasses import dataclass  # (1.4)
from datetime import date
from typing import Any  # "any type". Java: Object

from pydantic import BaseModel, ConfigDict, field_validator

ORDERS = {"A-1001": "shipped on 2026-11-10, arrives 2026-11-14",
          "A-1002": "waiting for payment"}  # a fake database


class MultiplyArgs(BaseModel):
    """Two numbers to multiply."""

    model_config = ConfigDict(extra="forbid")  # unknown keys = error (3.2)
    a: float
    b: float


class OrderArgs(BaseModel):
    """The order to look up."""

    model_config = ConfigDict(extra="forbid")
    order_id: str

    @field_validator("order_id")  # (1.6)
    @classmethod
    def forgive_digits(cls, value: str) -> str:
        """Accept "1001" as "A-1001" (the model drops the A-, part 2); reject the rest.

        The rule lives here, not in the schema the model reads (3.2 part 3).
        Args:
            value: e.g. "1001" or "A-1001".
        Returns:
            e.g. "A-1001".
        Raises:
            ValueError: e.g. "B-7". pydantic turns it into a ValidationError.
        """
        if value.isdigit():
            value = "A-" + value
        if not re.fullmatch(r"A-\d{4}", value):  # A, dash, 4 digits
            raise ValueError("order_id must look like A-1001")
        return value


class NoArgs(BaseModel):
    """No arguments."""

    model_config = ConfigDict(extra="forbid")


def multiply(args: MultiplyArgs) -> str:
    """Exact product as text.

    Args:
        args: e.g. MultiplyArgs(a=4821, b=3967).
    Returns:
        e.g. "19124907" (not "19124907.0"), or "7.5".
    """
    product = args.a * args.b
    if product.is_integer():
        return str(int(product))
    return str(product)


def order_status(args: OrderArgs) -> str:
    """The order's status, or an error text the model can pass on.

    Args:
        args: e.g. OrderArgs(order_id="A-1001").
    Returns:
        e.g. "shipped on 2026-11-10, arrives 2026-11-14", or "error: no order A-9999".
    """
    return ORDERS.get(args.order_id, f"error: no order {args.order_id}")


def today(args: NoArgs) -> str:
    """Today's date. The model can't know it (2.1: it only knows its training data).

    Args:
        args: NoArgs() (every tool takes one args object).
    Returns:
        e.g. "2026-11-13".
    """
    return date.today().isoformat()


@dataclass
class Tool:
    """What the model reads (description + args schema) and what code runs.

    Java: record Tool(String description, Class<?> argsModel, Function<?, String> function)
    """

    description: str
    args_model: type[BaseModel]  # the class itself, not an object
    function: Callable[[Any], str]  # takes the checked args, returns text


# Part 2 measured: an order description with no example -> the model stopped calling it.
TOOLS: dict[str, Tool] = {
    "multiply": Tool("Multiply two numbers exactly, e.g. 4821 * 3967.", MultiplyArgs, multiply),
    "order_status": Tool("Look up an order by its id, e.g. A-1001.", OrderArgs, order_status),
    "today": Tool("Today's date, e.g. 2026-11-13.", NoArgs, today),
}
