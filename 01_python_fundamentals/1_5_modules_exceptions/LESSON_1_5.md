# 1.5 Modules, imports, exceptions (~1.5 h)

Read this, run [examples_1_5_1_modules.py](examples_1_5_1_modules.py) (no network) and
[examples_1_5_2_exceptions.py](examples_1_5_2_exceptions.py) (Ollama on, ~3 s),
then fill in [chat_errors_1_5.py](chat_errors_1_5.py) and [exercises_1_5.py](exercises_1_5.py).

All numbers **measured on BISWAS**, Ollama 0.40.14, 2026-11-08, one run each
unless a range is given.

## The question of this lesson
You have used both ideas in every lesson without the names:
- Every exercises file starts with `from lab_tools.check import check`
  and ends with `if __name__ == "__main__":`. What do those two lines do?
- 1.7: a missing file gave `FileNotFoundError`. A dead port gave
  `ConnectTimeout`. 2.4: you wrote `raise ValueError(...)` yourself.

Why now: in 2.6 the chatbot (`assistant/` v1) is **several files** that
import each other. It must also **not crash** when Ollama is off. It should
print a tip instead. This lesson gives you both parts.

## Java → Python map
| Java | Python |
|---|---|
| one `.java` file = one class | one `.py` file = one **module** (many functions, constants, classes) |
| package = folder | package = folder + `__init__.py` (see `lab_tools/`) |
| `import a.b.C;` | `from a.b import C` |
| `import static a.B.f;` | `from a.b import f` |
| classpath | `sys.path` |
| `public static void main` | `if __name__ == "__main__":` |
| `private` | leading `_name` (a hint only, not enforced) |
| `try / catch / finally` | `try / except / else / finally` |
| `throw new X("msg", cause)` | `raise X("msg") from cause` |
| `class X extends RuntimeException` | `class X(Exception):` |
| checked exceptions (`throws`) | none: nothing forces a catch |

## 1. A file is a module, and importing runs it
Example part 1, section 1. `import prompts_1_5` runs that file from top
to bottom **once**. Its `print` shows on the first import only. A second
import gives back the same object (`again is prompts_1_5` → `True`).
Java runs nothing when you import. Python runs the file. So a module
should only *define* things at the top level, not *do* things.

## 2. Three import styles
| Style | Then write | Use when |
|---|---|---|
| `import prompts_1_5` | `prompts_1_5.build_messages(...)` | many names from one module |
| `from prompts_1_5 import build_messages` | `build_messages(...)` | one or two names (what `lab_tools.check` does) |
| `import numpy as np` | `np.array(...)` | long names, a common short form (4.1) |

Never `from x import *`. You can't tell where a name came from.

## 3. `if __name__ == "__main__":`, explained at last
Every module has a `__name__`. Run directly, it is `"__main__"`. Imported,
it is the module's own name (`'prompts_1_5'`, measured). So the checks at
the bottom of each exercises file run when *you* run the file. They don't
run when another file imports it. In 2.6 the chatbot's `main.py` uses this.
Its helper modules don't need it.

## 4. Where Python looks: `sys.path` (= classpath)
- **First, the folder of the file you ran.** That's why `exercises_1_5.py`
  can `import chat_errors_1_5`: the two files sit side by side.
- **Then `.venv`.** `uv sync` installed `lab_tools` there (pyproject.toml).
  That's why every lesson folder can import it.
- A folder name must be a valid Python name to be imported:
  `"01_python_fundamentals".isidentifier()` → `False` (it starts with a
  digit). Lesson folders are for running, not importing. `assistant/` in
  2.6 will have an importable name.

## 5. Exceptions you already met
| Lesson | What happened | Exception | Parent |
|---|---|---|---|
| 1.7 | missing file | `FileNotFoundError` | `OSError` |
| 1.7 | nothing on the port | `httpx.ConnectTimeout` | `TimeoutException` → `TransportError` |
| 1.7 | `raise_for_status()` on 404 | `httpx.HTTPStatusError` | `httpx.HTTPError` |
| 2.3 API | `reply["message"]` on a 404 reply `{"error": ...}` | `KeyError` | `LookupError` |
| 2.4 | your `temperature < 0` | `ValueError` | `Exception` |
| example 2, section 6 | `json.loads("{temperature: 0.2}")` | `JSONDecodeError` | `ValueError` |

There are no checked exceptions. Nothing forces you to catch any of these,
so a docstring should say what a function raises.

## 6. try / except / else / finally
Example part 2, section 2 hits the real 404:
`status 404 | model 'no-such-model' not found`.
- `except A:` blocks are tried **in order, first match wins**. Put the
  child before the parent. `except TransportError` also catches its child
  `ConnectTimeout`.
- `else:` runs only if the `try` had no error. Java has no twin.
- `finally:` always runs (like Java). For files, `with` (1.7) does this for you.

## 7. Your own errors + `raise ... from`
Ollama's raw errors (`ConnectTimeout`, a 404, a `KeyError`) tell you
*what broke*, not *what to do*. So we wrap them:
```python
class OllamaError(Exception): ...           # our base
class OllamaDownError(OllamaError): ...     # (Parent) = extends
raise OllamaDownError(f"no Ollama at {url}") from error
```
`from error` keeps the original as `__cause__` (measured:
`cause: ConnectTimeout`). Java: `new X(msg, cause)`. Callers catch
`OllamaError` and get every child. Same idea next: pydantic's
`ValidationError` when the model's JSON is wrong (3.2), tool errors and
retries (6.2).

## 8. Where to catch
- **Catch at the edge, where you can do something useful.** For example,
  the 2.6 chat loop prints "Start Ollama: ollama serve". `ask()` deep
  inside should raise, not print.
- **Don't catch what you can't fix.** A missing settings file → use the
  defaults (fixable). A broken settings file → let it go up (no good guess).
- Two styles. Look first: `if key in d:`, the Java style. Just try:
  `try: d[key] except KeyError:`, the common Python style. For dicts
  `d.get(key, default)` does it in one call.

## 9. Exercises
Two files. [chat_errors_1_5.py](chat_errors_1_5.py) is your module: fix 2 class
parents, write `answer_from`. [exercises_1_5.py](exercises_1_5.py) imports it: 4
functions, 16 checks. Checks 1–11 need no network. 12–16 call qwen3:1.7b.
14 and 15 wait 1 s on a dead port. That's the `connect=1.0` timeout.
Reference: 16/16 in 4.3–4.7 s (3 runs).
