# 1.2 Syntax vs Java (~2 h)

Read this, run [examples_1_2.py](examples_1_2.py), then solve [exercises_1_2.py](exercises_1_2.py).

## Biggest differences
| Java | Python |
|---|---|
| `{ }` blocks | indentation (4 spaces) + `:` |
| `;` ends a line | no `;` |
| `int x = 5;` | `x = 5` (type lives on the value) |
| `final` | no keyword; UPPER_CASE by convention |
| `null` | `None` |
| `true` / `false` | `True` / `False` |
| `&&` `\|\|` `!` | `and` `or` `not` |
| `a.equals(b)` | `a == b` (value); `a is b` = same object |
| `"a" + n` | `f"a{n}"` (f-string) |
| `for (int i=0;i<n;i++)` | `for i in range(n):` |
| `for (String s : list)` | `for s in items:` |
| `switch` | `match` (3.10+) or `if/elif/else` |
| `x > 0 ? a : b` | `a if x > 0 else b` |
| `i++` | `i += 1` (no `++`) |
| `7 / 2` → 3 | `7 / 2` → 3.5; `7 // 2` → 3 |
| overloading | default + keyword args |

## Functions
```python
def area(width: float, height: float = 1.0) -> float:
    return width * height

area(3)                 # 3.0  (default used)
area(height=2, width=3) # keyword args, any order
```
Type hints are **not enforced** at runtime. They help the IDE and tools.

## Truthy / falsy
Empty things are false: `0`, `""`, `[]`, `{}`, `None`.
`if items:` means "if the list is not empty".

## Multiple return values
```python
def min_max(nums): return min(nums), max(nums)
lo, hi = min_max([3, 1, 4])   # tuple unpacking
```

## Do it
1. `uv run python 01_python_fundamentals/1_2_syntax/examples_1_2.py`
2. Edit `exercises_1_2.py`: replace each `...` with code.
3. `uv run python 01_python_fundamentals/1_2_syntax/exercises_1_2.py`
   → all lines say PASS.

## Done when
- [ ] All exercises PASS.
- [ ] You can explain `/` vs `//`, `==` vs `is`, truthy values.
