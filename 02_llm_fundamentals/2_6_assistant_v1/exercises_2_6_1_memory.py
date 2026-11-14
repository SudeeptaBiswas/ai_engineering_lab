"""Tests for assistant/memory.py: what the model gets sent, and the token budget. No Ollama.

  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_1_memory.py -v
"""

import pytest

from assistant.memory import ChatMemory, Message
from lab_tools.log import debug, log

SYSTEM_PROMPT = "Be brief."  # 9 characters -> 3 tokens (ceil(9 / 4))
SYSTEM_MESSAGE: Message = {"role": "system", "content": SYSTEM_PROMPT}
LARGE_BUDGET = 100  # big enough that nothing is dropped


def message_texts(memory: ChatMemory) -> list[str]:
    """Take just the texts of memory.messages_to_send(), to keep the asserts short.

    Args:
        memory: e.g. a ChatMemory with SYSTEM_PROMPT + "hi".
    Returns:
        e.g. ["Be brief.", "hi"].
    """
    texts: list[str] = []
    for message in memory.messages_to_send():
        texts.append(message["content"])
    return texts


@debug
def test_new_memory_sends_only_the_system_message() -> None:
    """Checks: a new chat sends the rules and nothing else."""
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    sent_messages = memory.messages_to_send()
    log.debug("expected=%s got=%s", [SYSTEM_MESSAGE], sent_messages)
    assert sent_messages == [SYSTEM_MESSAGE]


@debug
def test_messages_keep_their_order_and_roles() -> None:
    """Checks: system first, then oldest -> newest, each with its role. The model reads them in this order."""
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    memory.add_message("user", "hi")
    memory.add_message("assistant", "hello")
    expected_messages: list[Message] = [SYSTEM_MESSAGE, {"role": "user", "content": "hi"},
                                        {"role": "assistant", "content": "hello"}]
    sent_messages = memory.messages_to_send()
    log.debug("expected=%s got=%s", expected_messages, sent_messages)
    assert sent_messages == expected_messages


@debug
def test_messages_to_send_is_a_copy() -> None:
    """Checks: adding to the returned list (as a tool round does) leaves the memory unchanged."""
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    sent_messages = memory.messages_to_send()
    sent_messages.append({"role": "tool", "tool_name": "today", "content": "2026-11-15"})
    messages_after = memory.messages_to_send()
    log.debug("expected=%s got=%s", [SYSTEM_MESSAGE], messages_after)
    assert messages_after == [SYSTEM_MESSAGE]


@pytest.mark.parametrize("bad_role", [
    "system",    # the rules are set once, in __init__
    "assitant",  # a typo must fail loudly, not be sent
    "",          # empty role
])
def test_add_message_rejects_bad_role(bad_role: str) -> None:
    """Checks: only "user" and "assistant" may be added.

    Args:
        bad_role: a role add_message must refuse.
    """
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    with pytest.raises(ValueError):
        memory.add_message(bad_role, "hi")


@debug
def test_token_count_includes_the_system_message() -> None:
    """Checks: the budget counts the rules too: 3 (system) + 2 ("hello", 5 characters) = 5."""
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    memory.add_message("user", "hello")
    token_count = memory.estimated_token_count()
    log.debug("expected=5 got=%d", token_count)
    assert token_count == 5


@debug
def test_over_budget_drops_the_oldest_first() -> None:
    """Checks: budget 9: 3 + 1 + 2 + 2 = 8 fits; a 4th message makes 10, so the oldest goes."""
    memory = ChatMemory(SYSTEM_PROMPT, max_history_tokens=9)
    memory.add_message("user", "one!")          # 4 characters -> 1 token
    memory.add_message("assistant", "two two")  # 7 characters -> 2 tokens
    memory.add_message("user", "three 3")       # 2 tokens. Total 3 + 1 + 2 + 2 = 8
    memory.add_message("assistant", "four 4!")  # 2 tokens -> 10 > 9: drop "one!"
    expected_texts = [SYSTEM_PROMPT, "two two", "three 3", "four 4!"]
    texts = message_texts(memory)
    log.debug("expected=%s got=%s", expected_texts, texts)
    assert texts == expected_texts
    assert memory.estimated_token_count() <= 9


@debug
def test_one_huge_message_is_kept_alone() -> None:
    """Checks: a message bigger than the whole budget is kept, the rest dropped.

    Sending nothing would be worse: the user's question would vanish.
    """
    memory = ChatMemory(SYSTEM_PROMPT, max_history_tokens=5)
    memory.add_message("user", "hi")
    long_question = "why " * 50  # 200 characters = 50 tokens
    memory.add_message("user", long_question)
    texts = message_texts(memory)
    log.debug("expected 2 texts, got %d", len(texts))
    assert texts == [SYSTEM_PROMPT, long_question]


@debug
def test_forget_chat_keeps_the_rules() -> None:
    """Checks: /reset forgets questions and answers but keeps the system message."""
    memory = ChatMemory(SYSTEM_PROMPT, LARGE_BUDGET)
    memory.add_message("user", "hi")
    memory.add_message("assistant", "hello")
    memory.forget_chat()
    sent_messages = memory.messages_to_send()
    log.debug("expected=%s got=%s", [SYSTEM_MESSAGE], sent_messages)
    assert sent_messages == [SYSTEM_MESSAGE]
