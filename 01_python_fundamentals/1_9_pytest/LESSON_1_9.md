# 1.9 pytest (~1 h)

Read this, run [examples_1_9_1_basics.py](examples_1_9_1_basics.py) (no Ollama) and
[examples_1_9_2_fakes.py](examples_1_9_2_fakes.py), then solve
[exercises_1_9_1_cosine.py](exercises_1_9_1_cosine.py) and [exercises_1_9_2_ollama.py](exercises_1_9_2_ollama.py).

All numbers **measured on 10284Sudee**, pytest 9.2.0, Ollama 0.40.15,
2026-11-09, one run each unless a range is given.

## The question of this lesson
Since 1.2 every exercise used `check()` from `lab_tools`. It works, but:
- Every check runs in one script. You can't run just one, or skip the slow ones.
- No way to fake Ollama: Ollama off means everything FAILs.
- No real project uses it. Every Python job uses **pytest**.

From 2.6 on, exercises use pytest (DECISIONS.md, 2026-11-09). `check()`
stays in the old lessons.

## Java → Python map
| Java (JUnit 5 / Mockito) | Python (pytest) |
|---|---|
| `@Test void average()` | `def test_average():` (the name is the marker) |
| `assertEquals(2.0, x)` | `assert x == 2.0` |
| `assertEquals(0.15, x, 1e-6)` | `assert x == pytest.approx(0.15)` |
| `assertThrows(X.class, () -> f())` | `with pytest.raises(X): f()` |
| `@ParameterizedTest @CsvSource` | `@pytest.mark.parametrize(...)` |
| `@BeforeEach` filling a field | `@pytest.fixture` + a parameter with its name |
| `when(c.get(any())).thenReturn(r)` | `monkeypatch.setattr(httpx, "get", fake_get)` |
| `@Tag("slow")` + `excludeTags` | `@pytest.mark.ollama` + `-m "not ollama"` |

## 1. A test = a function named `test_...` with an `assert`
```python
def test_average_of_three() -> None:
    assert average([1.0, 2.0, 3.0]) == 2.0
```
- pytest finds every function starting with `test_` and runs it.
- No `assertEquals` family: plain `assert`. pytest rewrites it so a
  failure shows both sides. Measured, after changing `2.0` to `2.5`:

```
>       assert average([1.0, 2.0, 3.0]) == 2.5
E       assert 2.0 == 2.5
E        +  where 2.0 = average([1.0, 2.0, 3.0])
1 failed, 6 passed in 0.08s
```

## 2. Run it
From the repo root:

| Command | What it does |
|---|---|
| `uv run pytest <file> -v` | one line per test, PASSED / FAILED |
| `uv run pytest <file> -q` | dots only: `.` pass, `F` fail |
| `uv run pytest <file> -k cosine` | only tests with "cosine" in the name |
| `uv run pytest <file> -x` | stop at the first FAIL |
| `uv run pytest <file> -m "not ollama"` | skip tests marked `ollama` |

Measured: part 1 examples **7 passed in 0.07 s**.

## 3. Floats: `pytest.approx`
`(0.1 + 0.2) / 2` is `0.15000000000000002`, so `== 0.15` is False.
`pytest.approx(0.15)` allows a tiny error. `approx(0.995, abs=0.001)` sets
the allowed error yourself (needed when the expected value is rounded).

## 4. Errors: `pytest.raises`
```python
with pytest.raises(ValueError, match="empty list"):
    average([])
```
Passes only if that error happens inside the `with`. No error is a FAIL.
`match=` searches the message (a regex).

## 5. One test, many rows: `parametrize`
```python
@pytest.mark.parametrize(("text", "expected_count"), [("the cat sat", 3), ("", 0)])
def test_word_count(text: str, expected_count: int) -> None:
    assert word_count(text) == expected_count
```
Each row runs as its own test: `test_word_count[the cat sat-3] PASSED`.
One bad row doesn't hide the others.

## 6. Shared data: fixtures
A function marked `@pytest.fixture` runs **before** each test that has a
parameter with the same name. Its return value is that parameter.
`monkeypatch` (next section) is a fixture that comes with pytest.

> ▶ **Now run part 1** and read the file next to the output (expect 7 passed):
> `uv run pytest 01_python_fundamentals/1_9_pytest/examples_1_9_1_basics.py -v`

## 7. Fakes: `monkeypatch`
```python
def test_model_names_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, timeout: float) -> httpx.Response:
        return httpx.Response(200, json={"models": [...]}, request=httpx.Request("GET", url))
    monkeypatch.setattr(httpx, "get", fake_get)  # for this test only
    assert model_names() == [...]
```
- While the test runs, `httpx.get` **is** `fake_get`. Afterwards pytest
  puts the real one back.
- `request=` is needed: `raise_for_status()` reads the URL from it.
- **Swap the name where it's looked up.** `search()` calls `embed` from its
  own module, so patch `search_module.embed`, not a copy you imported.

Why fakes (you asked):

| | Real Ollama | Fake |
|---|---|---|
| Ollama off | FAIL | still runs |
| Tests | Ollama + your code | your code only |
| Error cases (404, 501) | need a broken setup | one line |
| Answers | can shift with a model update | fixed |

So: fakes for **your** logic, one real test to prove Ollama agrees.
That's how work projects do it too.

## 8. Markers: label the real test
`@pytest.mark.ollama` is a label, declared in `pyproject.toml`.
`-m "not ollama"` skips it. Measured, part 2 examples:
**3 passed in 0.42 s** with Ollama, **2 passed, 1 deselected in 0.09 s** without.

> ▶ **Now run part 2** and read the file next to the output (expect 3 passed):
> `uv run pytest 01_python_fundamentals/1_9_pytest/examples_1_9_2_fakes.py -v`

## 9. Setup in this repo
`pyproject.toml` adds the 2.5 folder to the import path (`pythonpath` for
pytest, `extraPaths` for pyright). That's how a 1.9 test can do
`from exercises_2_5_1_cosine import cosine`. Folders starting with a digit
can't be Python packages, so a normal `import 02_llm...` is impossible.

## Exercises
You test **your own 2.5 code**. Each stub is `pytest.fail("not written yet")`
because a test with no assert **passes**: an empty test that says PASS
is worse than none.

1. [exercises_1_9_1_cosine.py](exercises_1_9_1_cosine.py): 6 tests (assert, raises,
   parametrize, approx). Add the 2 missing parametrize rows.
2. [exercises_1_9_2_ollama.py](exercises_1_9_2_ollama.py): 4 tests with fakes, 1 real.
   `test_embed_sends_model` catches the bug you fixed in 2.5 (wrong model sent).

Done = all pass with `-v`. Reference solution, measured:
**14 passed in 0.93–3.64 s** (3 runs; the first was the slow one),
**13 passed, 1 deselected in 0.62 s** with `-m "not ollama"`.
