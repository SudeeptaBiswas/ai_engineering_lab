"""Replace each `...` with code. Run until every line says PASS.

These classes are the start of a real chatbot — you will reuse them in 2.6.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system", "user" or "assistant"
    content: str

    def to_dict(self) -> dict[str, str]:
        """Return {"role": ..., "content": ...} — the shape LLM APIs expect."""
        return {"role": self.role, "content" : self.content}


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list[Message])

    def add(self, role: str, content: str) -> None:
        """Append a new Message."""
        self.messages.append(Message(role, content))

    def last(self, n: int) -> list[Message]:
        """The last n messages, oldest first. Hint: slicing."""
        return self.messages[-n:]

    def __len__(self) -> int:
        return len(self.messages)


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
    def run(self, arg: str) -> str:
        return arg.upper()


class ReverseTool(Tool):
    """run("abc") -> "cba". Hint: slicing with a negative step."""
    def run(self, arg: str) -> str:
        return arg[::-1]


def run_all(tools: list[Tool], arg: str) -> list[str]:
    """Run every tool on arg, return the results in order."""
    return [ tool.run(arg) for tool in tools ]


# ---------- Test helper — no need to change anything below ----------
# fn is a lambda (Java: () -> ...). It runs inside try, so an error in
# unfinished code prints FAIL instead of stopping the whole file.
# Callable[[], object] = takes nothing, returns anything. Java: Supplier<Object>
def check(label: str, fn: Callable[[], object], expected: object) -> None:
    try:
        got = fn()  # call the lambda now
        # {got!r} prints the value in code form, e.g. 'abc' with quotes
        status = "PASS" if got == expected else f"FAIL (got {got!r}, expected {expected!r})"
    except Exception as e:  # Java: catch (Exception e)
        status = f"FAIL ({type(e).__name__}: {e})"
    print(f"{label:<16} {status}")  # :<16 = pad label to 16 chars, left-aligned


def _conversation() -> Conversation:  # builds a 3-message conversation for tests
    conv = Conversation()
    conv.add("system", "be brief")
    conv.add("user", "hi")
    conv.add("assistant", "hello")
    return conv


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("to_dict", lambda: Message("user", "hi").to_dict(), {"role": "user", "content": "hi"})
    check("conv len", lambda: len(_conversation()), 3)
    check("conv last", lambda: [m.content for m in _conversation().last(2)], ["hi", "hello"])
    check("doc equal", lambda: Document("a", "x") == Document("a", "x"), True)
    check("doc in set", lambda: len({Document("a", "x"), Document("a", "x")}), 1)
    check("upper", lambda: UpperTool().run("hi"), "HI")
    check("reverse", lambda: ReverseTool().run("abc"), "cba")
    check("run_all", lambda: run_all([UpperTool(), ReverseTool()], "rag"), ["RAG", "gar"])
