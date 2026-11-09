"""Chat memory: the history the model gets, resent every turn.

The model remembers nothing between calls (lesson 2.3). This class keeps
the chat and hands it out each turn. When it grows past a token budget,
the oldest messages go (lesson 2.1), before Ollama cuts silently (2.6 part 1).

YOUR PART: replace each `raise NotImplementedError` with code.
Spec = 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_1_memory.py
"""

import math  # math.ceil = round up. Java: Math.ceil
from typing import TypedDict


class Message(TypedDict):
    """One chat message, the shape Ollama wants (lesson 2.6 part 2).

    Java: record Message(String role, String content) {}
    """

    role: str  # "system", "user" or "assistant"
    content: str  # the text


ROLES = ("user", "assistant")  # what add() accepts; the system message is set once


def estimate_tokens(text: str) -> int:
    """Rough token count: ~4 characters = 1 token, rounded up (lesson 2.1).

    Real counts are higher (part 1 measured 33 real vs 16 estimated), so
    the budget in cli.py stays well under num_ctx.
    Args:
        text: e.g. "hello" (5 characters).
    Returns:
        e.g. 2.
    """
    return math.ceil(len(text) / 4)


class ChatMemory:
    """The system message + the chat so far, kept under max_tokens.

    Java: a class with a final field `system` and a List<Message> history.
    """

    def __init__(self, system_prompt: str, max_tokens: int) -> None:
        """Start with no chat, only the rules.

        Args:
            system_prompt: e.g. "Be brief."
            max_tokens: budget for messages() by estimate_tokens, e.g. 2000.
        """
        self.system_message: Message = {"role": "system", "content": system_prompt}
        self.max_tokens = max_tokens
        self.history: list[Message] = []  # user + assistant messages, oldest first

    def messages(self) -> list[Message]:
        """What to send to the model: system message first, then the history.

        Must be a NEW list: the caller may change it (test_messages_is_a_copy).
        Returns:
            e.g. [{"role": "system", ...}, {"role": "user", "content": "hi"}].
        """
        raise NotImplementedError("2.6: write messages()")

    def token_count(self) -> int:
        """Estimated tokens of everything messages() returns.

        Returns:
            Sum of estimate_tokens(content) over all messages, system included.
        """
        raise NotImplementedError("2.6: write token_count()")

    def add(self, role: str, content: str) -> None:
        """Append one message to the history, then trim().

        Args:
            role: "user" or "assistant".
            content: the text.
        Raises:
            ValueError: role not in ROLES (e.g. "assitant"). Java: IllegalArgumentException
        """
        raise NotImplementedError("2.6: write add()")

    def trim(self) -> None:
        """Drop the OLDEST history message while token_count() > max_tokens.

        Never drops the system message (it is not in history) and never the
        newest message, even if it alone is over budget.
        Hint: a while loop; list.pop(0) removes the first item.
        """
        raise NotImplementedError("2.6: write trim()")

    def reset(self) -> None:
        """Forget the chat (/reset). The system message stays."""
        raise NotImplementedError("2.6: write reset()")
