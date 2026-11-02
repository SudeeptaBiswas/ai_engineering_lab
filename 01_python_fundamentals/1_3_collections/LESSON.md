# 1.3 Collections (~2 h)

Read this, run [examples.py](examples.py), then solve [exercises.py](exercises.py).

## Java → Python map
| Java | Python | Literal |
|---|---|---|
| `ArrayList<T>` | `list` | `[1, 2, 3]` |
| `HashMap<K,V>` | `dict` (keeps insert order) | `{"a": 1}` |
| `HashSet<T>` | `set` | `{1, 2}` (empty: `set()`) |
| `List.of(...)` / record | `tuple` (immutable) | `(1, "a")` |
| `list.size()` | `len(x)` | works on all four |
| `list.contains(x)` | `x in items` | fast on set/dict |
| `map.getOrDefault(k, d)` | `d.get(k, default)` | |
| `stream().map().filter()` | comprehension | see below |
| `Collections.sort(l, cmp)` | `sorted(items, key=..., reverse=True)` | |

## Slicing (no Java equivalent)
```python
nums = [0, 1, 2, 3, 4, 5]
nums[1:4]   # [1, 2, 3]   start inclusive, end exclusive
nums[:2]    # [0, 1]
nums[-2:]   # [4, 5]      negative = from the end
nums[::2]   # [0, 2, 4]   step
```

## Comprehensions = streams in one line
```python
[n * n for n in nums if n % 2 == 0]      # list
{w: len(w) for w in ["rag", "agent"]}    # dict
{w.lower() for w in ["A", "a", "B"]}     # set
```

## Handy built-ins
`enumerate`, `zip`, `sum`, `min`, `max`, `any`, `all`, `sorted`, `reversed`.
From `collections`: `Counter` (counting), `defaultdict` (auto-create values).

## Gotcha: mutable default argument
```python
def add(item, bucket=[]):   # BUG: one list shared by every call
def add(item, bucket=None): # fix
    bucket = [] if bucket is None else bucket
```

## Do it
1. `uv run python 01_python_fundamentals/1_3_collections/examples.py`
2. Fill each `...` in `exercises.py`. Try comprehensions where they fit.
3. `uv run python 01_python_fundamentals/1_3_collections/exercises.py` → all PASS.

## Done when
- [ ] All exercises PASS.
- [ ] You can explain slicing, comprehensions, and when to pick set vs list.
