# Review: phase 01, Python for Java devs

Per topic: the **flow**, the **must-remember** points, then a **quiz**.
Click a question to see the answer. Say your answer first.
Keywords: [GLOSSARY_PYTHON.md](GLOSSARY_PYTHON.md).

## 1.1 Setup: uv, venv
```
pyproject.toml (deps) → uv sync → .venv (packages) + uv.lock (exact versions)
                      → uv run python file.py   (no "activate" needed)
```
<details><summary>Q1. pyproject.toml / uv.lock / .venv in Java terms?</summary>pom.xml / Gradle lockfile / a per-project ~/.m2 (git-ignored).</details>

## 1.2 Syntax vs Java
- Blocks by indentation + `:`. No `;`, no `++`. `None`, `True`, `and/or/not`.
- Type hints are **not enforced** at runtime; pyright checks them.

<details><summary>Q1. 7 / 2 vs 7 // 2?</summary>3.5 vs 3.</details>
<details><summary>Q2. == vs is?</summary>Same value vs same object (Java .equals() vs ==).</details>
<details><summary>Q3. What does `if items:` test?</summary>Not empty. 0, "", [], {}, None are falsy.</details>

## 1.3 Collections
```
list [..]  dict {k: v}  set {..} / set()  tuple (..)    len(x), x in y
```
- Slicing: start inclusive, end exclusive; negative = from the end.
- Comprehension = a stream in one line.

<details><summary>Q1. nums = [0..5]: nums[1:4], nums[-2:]?</summary>[1, 2, 3] and [4, 5].</details>
<details><summary>Q2. set or list for "x in items" on big data?</summary>set: fast lookup. list: keeps order + duplicates.</details>
<details><summary>Q3. What's wrong with def add(item, bucket=[])?</summary>One list shared by every call. Use bucket=None, then make a new list.</details>

## 1.4 Classes and dataclasses
- `self` = `this`, written out. `_x` = internal by convention only.
- `@dataclass` for data holders; plain class for behaviour.

<details><summary>Q1. What does @dataclass write for you?</summary>__init__, __repr__, __eq__.</details>
<details><summary>Q2. List default in a dataclass?</summary>field(default_factory=list). `= []` is an error.</details>
<details><summary>Q3. ABC vs duck typing?</summary>Duck: anything with .run() works. ABC: explicit contract, fails early if missing.</details>

## 1.5 Modules, imports, exceptions
```
import x → search sys.path (script folder, then .venv) → run x top to bottom ONCE → cache
error → except blocks in order (child before parent) → else (no error) → finally (always)
```
- A module should only *define* things at top level; importing runs it.
- Catch at the edge, where you can do something useful. Don't catch what you can't fix.

<details><summary>Q1. What is __name__ when run vs imported?</summary>"__main__" vs the module's own name.</details>
<details><summary>Q2. Why can't you import 01_python_fundamentals?</summary>Starts with a digit: not a valid Python name.</details>
<details><summary>Q3. raise OllamaDownError(...) from error keeps what?</summary>The original error, as __cause__ (Java: new X(msg, cause)).</details>
<details><summary>Q4. Checked exceptions in Python?</summary>None. Nothing forces a catch, so docstrings list Raises.</details>

## 1.6 Type hints + pydantic
```
JSON text → Model.model_validate_json → (field_validator mode="before" cleans)
  → hints become rules (Field, Literal, extra="forbid") → object, or ValidationError (all problems)
```
- Hints are notes: Python ignores them at runtime. pydantic checks them.
- Lax by default (`"3"` → 3, `true` → 1); `Field(strict=True)` refuses.
- Shape, not truth: `"bug"` on a billing ticket passes. Measure that (3.1, 5.1).
- One source of labels: `Label = Literal[...]`, `LABELS = list(get_args(Label))`.

<details><summary>Q1. A dataclass gets text=5. Error?</summary>No. Dataclasses don't check types; pydantic does.</details>
<details><summary>Q2. Unknown key "team" by default? How to refuse it?</summary>Ignored. ConfigDict(extra="forbid") → extra_forbidden.</details>
<details><summary>Q3. What is loc ("tags", 1)? And ()?</summary>The 2nd tag. () = the whole input, e.g. json_invalid.</details>
<details><summary>Q4. Why mode="before" on the label validator?</summary>Literal is case-sensitive: clean " Billing." to "billing" before the check.</details>
<details><summary>Q5. Why not Literal[*LABELS]?</summary>Literal needs fixed values pyright can see. Go the other way: get_args(Label).</details>

## 1.7 Files, JSON, HTTP
```
Path → open(encoding="utf-8") in `with` → text → json.loads → dict
httpx.post(url, json=dict, timeout=...) → status_code → raise_for_status() → .json()
```
<details><summary>Q1. Is a 404 an exception in httpx?</summary>No. Check status_code or call raise_for_status().</details>
<details><summary>Q2. Why 127.0.0.1, not localhost?</summary>On Windows localhost tries IPv6 first: 2.16 s vs 0.02 s per call.</details>
<details><summary>Q3. Catch ConnectError and ConnectTimeout together?</summary>Catch the parent, httpx.TransportError.</details>
<details><summary>Q4. open(p, "w") on an existing file?</summary>Wipes it first. "a" appends.</details>

## 1.9 pytest
```
uv run pytest file -v → find test_* functions → run fixtures → run test → assert
fake:  monkeypatch.setattr(module, "name", fake) → real code calls the fake → assert
spy:   fake writes down what it got (sent_bodies) → assert on what was SENT
```
- A test with no assert **passes**: stubs use `pytest.fail(...)`.
- Patch the name **where it is looked up** (`search_module.embed`).
- A call that should raise must be **inside** `with pytest.raises(...)`.
- Fakes test your logic (fast, no Ollama); one `@pytest.mark.ollama` test proves the real thing.

<details><summary>Q1. Why pytest.approx for 0.1 + 0.2?</summary>Floats aren't exact: (0.1 + 0.2) / 2 is 0.15000000000000002.</details>
<details><summary>Q2. Read test_x[vector_a2-vector_b2-1.0] FAILED?</summary>Row index 2 (the 3rd row) failed. Obtained = code's result, Expected = your row.</details>
<details><summary>Q3. Skip / run only the real-Ollama tests?</summary>-m "not ollama" / -m ollama.</details>
<details><summary>Q4. A test passes. How do you know it really tests something?</summary>Break the code or the expected value on purpose: it must FAIL.</details>
<details><summary>Q5. Why keep the spy's list inside the test?</summary>At module level it's shared by all tests and never emptied: results depend on order.</details>
