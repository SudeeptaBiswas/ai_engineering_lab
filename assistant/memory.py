"""Chat memory: the conversation the model gets again on every turn.

Why: the model remembers nothing between calls (lesson 2.3). So this class
keeps the chat and hands all of it over each turn. When the chat grows past
a token budget, the oldest messages are dropped (lesson 2.1), before Ollama
would cut them silently (lesson 2.6 part 1).

Only questions and final answers are kept here. Tool messages (v2) live for
one turn only, in chat_turn.py.

Tests: 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_1_memory.py
"""

import math  # math.ceil = round up
from typing import Any, NotRequired, TypedDict

from lab_tools.log import cut_text, debug, log

CHARACTERS_PER_TOKEN = 4  # rough rule from lesson 2.1
ROLES_ALLOWED_IN_HISTORY = ("user", "assistant")  # the system message is set once, in __init__


class Message(TypedDict):
    """One chat message, in the shape Ollama's /api/chat wants.

    Chat text needs only role + content. A tool round (v2) also uses
    tool_calls and tool_name.
    """

    role: str  # "system", "user", "assistant" or "tool"
    content: str  # the text
    tool_calls: NotRequired[list[dict[str, Any]]]  # only on an assistant message that asks for tools
    tool_name: NotRequired[str]  # only on a "tool" message: which tool this result came from


def estimate_tokens(text: str) -> int:
    """Guess how many tokens a text is, without asking the model.

    How: about 4 characters = 1 token, rounded up (lesson 2.1). Real counts
    are higher (2.6 part 1: 33 real vs 16 estimated), so the budget in
    cli.py stays well under the model's context size.
    Args:
        text: e.g. "hello" (5 characters).
    Returns:
        e.g. 2.
    """
    token_estimate = math.ceil(len(text) / CHARACTERS_PER_TOKEN)
    return token_estimate


class ChatMemory:
    """The system message plus the chat so far, kept under a token budget."""

    def __init__(self, system_prompt: str, max_history_tokens: int) -> None:
        """Start a new chat: only the rules, no messages yet.

        Args:
            system_prompt: the rules for the model, e.g. "Be brief.".
            max_history_tokens: budget for messages_to_send(), e.g. 2000.
        """
        self.system_message: Message = {"role": "system", "content": system_prompt}
        self.max_history_tokens = max_history_tokens
        self.history: list[Message] = []  # user + assistant messages, oldest first

    def messages_to_send(self) -> list[Message]:
        """Give the messages for the next model call: system message first, then the chat.

        It is a NEW list each time, so the caller can add tool messages to it
        without changing the memory (test_messages_to_send_is_a_copy).
        Returns:
            e.g. [{"role": "system", ...}, {"role": "user", "content": "hi"}].
        """
        messages_for_model: list[Message] = [self.system_message]
        for message in self.history:
            messages_for_model.append(message)
        # --- explicit end ---
        # concise: messages_for_model = [self.system_message, *self.history]
        return messages_for_model

    def estimated_token_count(self) -> int:
        """Guess the tokens of everything messages_to_send() returns.

        Returns:
            Sum of estimate_tokens(content) over all messages, system included, e.g. 5.
        """
        total_tokens = 0
        for message in self.messages_to_send():
            total_tokens += estimate_tokens(message["content"])
        return total_tokens

    @debug
    def add_message(self, role: str, content: str) -> None:
        """Save one message at the end of the chat, then keep the chat under budget.

        Args:
            role: "user" or "assistant".
            content: the text, e.g. "What is RAG?".
        Raises:
            ValueError: role not allowed, e.g. "assitant" (a typo) or "system".
        """
        log.debug("start: role=%s content=%s", role, cut_text(content))
        if role not in ROLES_ALLOWED_IN_HISTORY:
            # {role!r} puts quotes around the text, so an empty "" is visible
            raise ValueError(f"role must be one of {ROLES_ALLOWED_IN_HISTORY}, got {role!r}")
        new_message: Message = {"role": role, "content": content}
        self.history.append(new_message)
        self.drop_oldest_until_under_budget()

    @debug
    def drop_oldest_until_under_budget(self) -> None:
        """Remove the oldest messages while the chat is over max_history_tokens.

        Never removes the system message (it is not in history) and never the
        newest message, even when it alone is over the budget: sending nothing
        would lose the user's question.
        """
        has_more_than_newest = len(self.history) > 1
        while self.estimated_token_count() > self.max_history_tokens and has_more_than_newest:
            dropped_message = self.history.pop(0)  # pop(0) = remove the first (oldest) item
            log.debug("dropped %s message: %s", dropped_message["role"], cut_text(dropped_message["content"]))
            has_more_than_newest = len(self.history) > 1
        log.debug("result: %d messages, ~%d tokens", len(self.history), self.estimated_token_count())

    def forget_chat(self) -> None:
        """Forget all questions and answers (the /reset command). The rules stay."""
        self.history = []
