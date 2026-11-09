"""Tests for assistant/memory.py. No Ollama. These tests are the spec:
fill the stubs in assistant/memory.py until all pass.

  uv run pytest 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_1_memory.py -v
"""

import pytest

from assistant.memory import ChatMemory, Message

SYSTEM = "Be brief."  # 9 chars -> 3 tokens (ceil(9 / 4))
SYSTEM_MESSAGE: Message = {"role": "system", "content": SYSTEM}


def contents(memory: ChatMemory) -> list[str]:
    """Just the texts of memory.messages(), to keep the asserts short.

    Args:
        memory: e.g. a ChatMemory with SYSTEM + "hi".
    Returns:
        e.g. ["Be brief.", "hi"].
    """
    texts: list[str] = []
    for message in memory.messages():
        texts.append(message["content"])
    return texts


def test_new_memory_has_only_system() -> None:
    """A new memory sends just the system message."""
    memory = ChatMemory(SYSTEM, max_tokens=100)
    assert memory.messages() == [SYSTEM_MESSAGE]


def test_add_keeps_order() -> None:
    """System first, then messages oldest -> newest, with their roles."""
    memory = ChatMemory(SYSTEM, max_tokens=100)
    memory.add("user", "hi")
    memory.add("assistant", "hello")
    assert memory.messages() == [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_messages_is_a_copy() -> None:
    """Changing the returned list must not change the memory (like 2.3 add_message)."""
    memory = ChatMemory(SYSTEM, max_tokens=100)
    sent = memory.messages()
    sent.append({"role": "user", "content": "sneaky"})
    assert memory.messages() == [SYSTEM_MESSAGE]


@pytest.mark.parametrize("bad_role", ["system", "assitant", ""])
def test_add_rejects_bad_role(bad_role: str) -> None:
    """Only "user" and "assistant" may be added; a typo must fail loudly.

    Args:
        bad_role: a role add() must refuse.
    """
    memory = ChatMemory(SYSTEM, max_tokens=100)
    with pytest.raises(ValueError):
        memory.add(bad_role, "hi")


def test_token_count_includes_system() -> None:
    """3 (system) + ceil(5 / 4) = 2 ("hello") = 5."""
    memory = ChatMemory(SYSTEM, max_tokens=100)
    memory.add("user", "hello")
    assert memory.token_count() == 5


def test_trim_drops_oldest_first() -> None:
    """Budget 9: 3 + 1 + 2 + 2 = 8 fits; a 4th message makes 10, so the oldest goes."""
    memory = ChatMemory(SYSTEM, max_tokens=9)
    memory.add("user", "one!")  # 4 chars -> 1 token
    memory.add("assistant", "two two")  # 7 chars -> 2 tokens (ceil 1.75)
    memory.add("user", "three 3")  # 2 tokens. Total 3 + 1 + 2 + 2 = 8
    memory.add("assistant", "four 4!")  # 2 tokens -> 10 > 9: drop "one!" -> 9
    assert contents(memory) == [SYSTEM, "two two", "three 3", "four 4!"]
    assert memory.token_count() <= 9


def test_trim_keeps_system_and_newest() -> None:
    """One message bigger than the whole budget: keep it anyway, drop the rest.

    Sending nothing would be worse than going over: the user's question
    would vanish. (Ollama itself then cuts at num_ctx, part 1.)
    """
    memory = ChatMemory(SYSTEM, max_tokens=5)
    memory.add("user", "hi")
    long_question = "why " * 50  # 200 chars = 50 tokens
    memory.add("user", long_question)
    assert contents(memory) == [SYSTEM, long_question]


def test_reset_keeps_system() -> None:
    """/reset forgets the chat but keeps the rules (system message)."""
    memory = ChatMemory(SYSTEM, max_tokens=100)
    memory.add("user", "hi")
    memory.add("assistant", "hello")
    memory.reset()
    assert memory.messages() == [SYSTEM_MESSAGE]
