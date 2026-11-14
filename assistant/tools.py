"""The 4 tools the model may ask for (v2). From lesson 3.3, plus refund from 3.4.

Each tool = an arguments model (pydantic checks what the model sent) + a
function that does the work and returns text for the model. Running them
and checking them: tool_runner.py and tool_gate.py.

Tests: 03_prompting_tools/3_5_assistant_v2/test_3_5_1_tools.py
"""

import re  # re.fullmatch = the whole text matches a pattern
from collections.abc import Callable  # the type of a function
from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

ORDER_STATUS_BY_ID = {"A-1001": "shipped on 2026-11-10, arrives 2026-11-14",
                      "A-1002": "waiting for payment"}  # a fake order database
ORDER_ID_PATTERN = r"A-\d{4}"  # "A", a dash, 4 digits


class MultiplyArguments(BaseModel):
    """The two numbers to multiply."""

    model_config = ConfigDict(extra="forbid")  # an unknown key is an error (3.2)
    a: float
    b: float


class OrderArguments(BaseModel):
    """The order to look up."""

    model_config = ConfigDict(extra="forbid")
    order_id: str

    @field_validator("order_id")  # runs on order_id while pydantic checks it (1.6)
    @classmethod
    def accept_digits_only_order_id(cls, order_id: str) -> str:
        """Accept "1001" as "A-1001" (the model drops the "A-", 3.3 part 2); reject other shapes.

        Args:
            order_id: e.g. "1001" or "A-1001".
        Returns:
            e.g. "A-1001".
        Raises:
            ValueError: e.g. "B-7". pydantic turns it into a ValidationError.
        """
        full_order_id = order_id
        if order_id.isdigit():
            full_order_id = "A-" + order_id
        if not re.fullmatch(ORDER_ID_PATTERN, full_order_id):
            raise ValueError("order_id must look like A-1001")
        return full_order_id


class RefundArguments(OrderArguments):
    """The order to refund and how much. order_id gets the same check as OrderArguments."""

    amount: float


class NoArguments(BaseModel):
    """For a tool that needs no input."""

    model_config = ConfigDict(extra="forbid")


def multiply(arguments: MultiplyArguments) -> str:
    """Multiply two numbers exactly (the model alone got 2 of 5 right, 3.3).

    Args:
        arguments: e.g. MultiplyArguments(a=4821, b=3967).
    Returns:
        e.g. "19124907" (not "19124907.0"), or "7.5".
    """
    product = arguments.a * arguments.b
    product_text = str(product)
    if product.is_integer():  # 19124907.0 -> "19124907"
        product_text = str(int(product))
    return product_text


def order_status(arguments: OrderArguments) -> str:
    """Look up an order's status in the fake database.

    Args:
        arguments: e.g. OrderArguments(order_id="A-1001").
    Returns:
        e.g. "shipped on 2026-11-10, arrives 2026-11-14", or "error: no order A-9999".
    """
    not_found_text = f"error: no order {arguments.order_id}"
    status_text = ORDER_STATUS_BY_ID.get(arguments.order_id, not_found_text)
    return status_text


def today(arguments: NoArguments) -> str:
    """Give today's date. The model can't know it (2.1: it only knows its training data).

    Args:
        arguments: NoArguments() (every tool takes one arguments object).
    Returns:
        e.g. "2026-11-15".
    """
    today_text = date.today().isoformat()
    return today_text


def refund(arguments: RefundArguments) -> str:
    """Pretend to refund money. FAKE: nothing is paid; it only returns the text.

    The gate (tool_gate.py) decides first whether this may run at all.
    Args:
        arguments: e.g. RefundArguments(order_id="A-1001", amount=20).
    Returns:
        e.g. "refund of 20.0 for order A-1001 recorded (fake: no money moved)".
    """
    refund_text = f"refund of {arguments.amount} for order {arguments.order_id} recorded (fake: no money moved)"
    return refund_text


@dataclass
class Tool:
    """One tool: what the model reads about it, and what our code runs."""

    description: str  # the model only reads this + the arguments schema (3.3 part 2)
    arguments_model: type[BaseModel]  # the class itself, e.g. OrderArguments
    function: Callable[[Any], str]  # takes the checked arguments object, returns text
    changes_data: bool  # True = needs the gate's OK (tool_gate.py); False = read-only


# 3.3 part 2: an order description without an example id -> the model stopped calling it.
TOOLS_BY_NAME: dict[str, Tool] = {
    "multiply": Tool("Multiply two numbers exactly, e.g. 4821 * 3967.", MultiplyArguments, multiply, False),
    "order_status": Tool("Look up an order by its id, e.g. A-1001.", OrderArguments, order_status, False),
    "today": Tool("Today's date, e.g. 2026-11-15.", NoArguments, today, False),
    "refund": Tool("Refund money for an order, e.g. order_id A-1001, amount 20.", RefundArguments, refund, True),
}
