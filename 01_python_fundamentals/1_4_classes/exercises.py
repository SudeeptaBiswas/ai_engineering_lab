"""Replace each `...` with code. Run until every line says PASS.

These classes are the start of a real chatbot — you will reuse them in 2.6.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system", "user" or "assistant"
    content: str

    def to_dict(self) -> dict[str, str]:
        """Return {"role": ..., "content": ...} — the shape LLM APIs expect."""
        ...


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        """Append a new Message."""
        ...

    def last(self, n: int) -> list[Message]:
        """The last n messages, oldest first. Hint: slicing."""
        ...

    def __len__(self) -> int:
        ...


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    score: float = 0.0


class Tool(ABC):
    @abstractmethod
    def run(self, arg: str) -> str: ...


class UpperTool(Tool):
    """run("hi") -> "HI"."""
    ...


class ReverseTool(Tool):
    """run("abc") -> "cba". Hint: slicing with a negative step."""
    ...


def run_all(tools: list[Tool], arg: str) -> list[str]:
    """Run every tool on arg, return the results in order."""
    ...


def check(label: str, fn, expected) -> None:
    try:
        got = fn()
        status = "PASS" if got == expected else f"FAIL (got {got!r}, expected {expected!r})"
    except Exception as e:  # unfinished code may raise; show it, keep going
        status = f"FAIL ({type(e).__name__}: {e})"
    print(f"{label:<16} {status}")


def _conversation() -> Conversation:
    conv = Conversation()
    conv.add("system", "be brief")
    conv.add("user", "hi")
    conv.add("assistant", "hello")
    return conv


if __name__ == "__main__":
    check("to_dict", lambda: Message("user", "hi").to_dict(), {"role": "user", "content": "hi"})
    check("conv len", lambda: len(_conversation()), 3)
    check("conv last", lambda: [m.content for m in _conversation().last(2)], ["hi", "hello"])
    check("doc equal", lambda: Document("a", "x") == Document("a", "x"), True)
    check("doc in set", lambda: len({Document("a", "x"), Document("a", "x")}), 1)
    check("upper", lambda: UpperTool().run("hi"), "HI")
    check("reverse", lambda: ReverseTool().run("abc"), "cba")
    check("run_all", lambda: run_all([UpperTool(), ReverseTool()], "rag"), ["RAG", "gar"])
