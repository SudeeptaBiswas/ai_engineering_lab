# 1.4 Classes and dataclasses (~2 h)

Read this, run [examples.py](examples.py), then solve [exercises.py](exercises.py).

## Java → Python map
| Java | Python |
|---|---|
| constructor | `def __init__(self, ...)` |
| `this` | `self` (always the first parameter, written out) |
| `private int x` | `self._x` — underscore = "internal", not enforced |
| getter | `@property` |
| `toString()` | `__repr__` (debug) / `__str__` (user-facing) |
| `equals()` / `hashCode()` | `__eq__` / `__hash__` |
| `record` / Lombok `@Data` | `@dataclass` |
| immutable record | `@dataclass(frozen=True)` |
| `extends A` | `class B(A):` |
| `super(...)` | `super().__init__(...)` |
| `interface` | `ABC` + `@abstractmethod`, or `Protocol` |
| `static` method | `@staticmethod` / `@classmethod` |
| `size()` on your class | `__len__` → `len(obj)` works |

## Plain class vs dataclass
```python
class Point:                      # plain: write it all yourself
    def __init__(self, x, y):
        self.x = x
        self.y = y

@dataclass                        # dataclass: __init__, __repr__, __eq__ for free
class Point:
    x: float
    y: float = 0.0
```
Use `@dataclass` for data holders (messages, documents, configs).
Use a plain class when the object mostly has behaviour.

## Gotcha: mutable defaults in dataclasses
`items: list = []` is an error. Use `items: list = field(default_factory=list)`.

## Duck typing
Python doesn't need `implements`. If it has `.run()`, you can call `.run()`.
`ABC` makes the contract explicit and fails early if a method is missing.

## Do it
1. `uv run python 01_python_fundamentals/1_4_classes/examples.py`
2. Fill each `...` in `exercises.py`.
3. `uv run python 01_python_fundamentals/1_4_classes/exercises.py` → all PASS.

## Done when
- [ ] All exercises PASS.
- [ ] You can explain `self`, `@dataclass`, `frozen=True`, and ABC vs duck typing.
