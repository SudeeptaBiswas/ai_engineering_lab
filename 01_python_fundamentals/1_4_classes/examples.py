"""Python classes next to Java. Run it, then read each block."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# Plain class: constructor, private-by-convention field, property, toString
class Counter:
    def __init__(self, start: int = 0):
        self._count = start  # underscore = internal

    def increment(self) -> None:
        self._count += 1

    @property
    def count(self) -> int:  # read like a field: c.count
        return self._count

    def __repr__(self) -> str:
        return f"Counter({self._count})"


c = Counter()
c.increment()
c.increment()
print(c, c.count)


# Dataclass: __init__, __repr__, __eq__ generated
@dataclass
class ModelInfo:
    name: str
    size_b: float
    tags: list[str] = field(default_factory=list)  # not tags=[]

    def label(self) -> str:
        return f"{self.name}:{self.size_b}b"


m1 = ModelInfo("qwen3", 4)
m2 = ModelInfo("qwen3", 4)
print(m1, m1.label(), "equal:", m1 == m2)


# Frozen dataclass = immutable record; can be a dict key or set item
@dataclass(frozen=True)
class Chunk:
    doc_id: str
    index: int


seen = {Chunk("a.pdf", 0), Chunk("a.pdf", 0), Chunk("a.pdf", 1)}
print("unique chunks:", len(seen))


# Inheritance + super()
class TimedCounter(Counter):
    def __init__(self, start: int = 0, label: str = "t"):
        super().__init__(start)
        self.label = label

    def __repr__(self) -> str:
        return f"TimedCounter({self.label}, {self.count})"


print(TimedCounter(5, "calls"))


# ABC = interface
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side**2


print("area:", Square(3).area())
try:
    Shape()
except TypeError as e:
    print("can't create ABC:", e)


# classmethod = alternate constructor (like a static factory)
@dataclass
class Settings:
    model: str
    temperature: float

    @classmethod
    def default(cls) -> "Settings":
        return cls("qwen3:4b", 0.2)


print(Settings.default())


# __len__ makes len() work on your class
class Box:
    def __init__(self):
        self.items: list[str] = []

    def __len__(self) -> int:
        return len(self.items)


b = Box()
b.items += ["x", "y"]
print("len(box):", len(b))
