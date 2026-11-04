"""Python classes next to Java. Run it, then read each block."""

from abc import ABC, abstractmethod  # ABC = "abstract base class"
from dataclasses import dataclass, field


# ---------- Plain class ----------
class Counter:
    # __init__ is the constructor. `self` = Java `this`, always written first.
    def __init__(self, start: int = 0):
        self._count = start  # fields are created by assigning to self.
        # _count: underscore means "internal, don't touch" (not enforced)

    def increment(self) -> None:  # -> None = Java `void`
        self._count += 1

    @property  # a getter you read like a field: c.count (no brackets)
    def count(self) -> int:
        return self._count

    def __repr__(self) -> str:  # Java toString(); print() uses it
        return f"Counter({self._count})"


c = Counter()  # no `new` keyword
c.increment()
c.increment()
print(c, c.count)


# ---------- Dataclass — like a Java record / Lombok @Data ----------
# Python writes __init__, __repr__ and __eq__ (equals) for you.
@dataclass
class ModelInfo:
    name: str  # field with a type
    size_b: float
    # default_factory=list -> a NEW empty list for each object.
    # (tags: list = [] would share one list between all objects.)
    tags: list[str] = field(default_factory=list[str])  # list[str]() -> []

    def label(self) -> str:
        return f"{self.name}:{self.size_b}b"


m1 = ModelInfo("qwen3", 4)
m2 = ModelInfo("qwen3", 4)
print(m1, m1.label(), "equal:", m1 == m2)  # == calls the generated __eq__


# ---------- Frozen dataclass = immutable record ----------
# frozen=True: fields can't change after creation, and the object gets
# a hash, so it can go in a set or be a dict key (like hashCode()).
@dataclass(frozen=True)
class Chunk:
    doc_id: str
    index: int


seen = {Chunk("a.pdf", 0), Chunk("a.pdf", 0), Chunk("a.pdf", 1)}
print("unique chunks:", len(seen))  # 2 — the duplicate is dropped


# ---------- Inheritance ----------
class TimedCounter(Counter):  # Java: class TimedCounter extends Counter
    def __init__(self, start: int = 0, label: str = "t"):
        super().__init__(start)  # Java: super(start)
        self.label = label

    def __repr__(self) -> str:  # override — no @Override needed
        return f"TimedCounter({self.label}, {self.count})"


print(TimedCounter(5, "calls"))


# ---------- ABC = Java interface / abstract class ----------
class Shape(ABC):
    @abstractmethod  # subclasses MUST implement this
    def area(self) -> float: ...  # `...` = empty body


class Square(Shape):  # Java: class Square implements Shape
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side**2  # ** = power


print("area:", Square(3).area())
try:  # try/except = Java try/catch
    Shape()  # pyright: ignore[reportAbstractUsage]  -- on purpose, shows the error
except TypeError as e:
    print("can't create ABC:", e)


# ---------- classmethod = static factory method ----------
@dataclass
class Settings:
    model: str
    temperature: float

    @classmethod  # Java: public static Settings defaults()
    def default(cls) -> "Settings":  # cls = the class itself (Settings)
        return cls("qwen3:4b", 0.2)  # same as Settings("qwen3:4b", 0.2)


print(Settings.default())


# ---------- __len__ makes len(obj) work ----------
class Box:
    def __init__(self):
        self.items: list[str] = []

    def __len__(self) -> int:  # Python calls this for len(box)
        return len(self.items)


b = Box()
b.items += ["x", "y"]  # += on a list = addAll
print("len(box):", len(b))
