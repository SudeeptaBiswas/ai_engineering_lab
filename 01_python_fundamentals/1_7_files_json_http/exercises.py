"""Replace each `...` with code. Run until every line says PASS.
Needs Ollama running with qwen3:4b pulled (`ollama list`)."""

import json  # pyright: ignore[reportUnusedImport] — json.dumps / json.loads
import tempfile  # temporary folder for the file tests
import traceback  # find the failing line, for check() below
from collections.abc import Callable  # type of a function, for check() below
from pathlib import Path
from typing import Any  # "any type": what json.loads returns. Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until you use it

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows


# ---------- Files + JSON ----------
def save_json(path: Path, data: Any) -> None:
    """Write data as pretty JSON (indent=2), UTF-8."""
    ...


def load_json(path: Path) -> Any:
    """Read a JSON file back into Python objects."""
    ...


def count_lines(path: Path) -> int:
    """Number of NON-blank lines. A line with only spaces is blank.
    Hint: read_text, splitlines, strip()."""
    ...


# ---------- HTTP (Ollama) ----------
def ollama_version() -> str:
    """GET /api/version -> "0.40.14" (the value only, not the dict)."""
    ...


def model_names() -> list[str]:
    """GET /api/tags -> names of all models, sorted A-Z."""
    ...


def model_size_gb(name: str) -> float | None:
    """Size from /api/tags in GB (bytes / 1_000_000_000), rounded to 1.
    None if that model is not on this PC."""
    ...


def is_installed(name: str) -> bool:
    """POST /api/show {"model": name}: 200 -> True, 404 -> False."""
    ...


def context_length(name: str) -> int:
    """POST /api/show -> model_info has a key like "qwen3.context_length"
    (the start depends on the model family). Find the key that ENDS with
    ".context_length" and return its value. Hint: str.endswith."""
    ...


def save_report(path: Path) -> None:
    """Files + JSON + HTTP together: write {model name: size in GB}
    for every model on this PC to `path` as JSON. Reuse your functions."""
    ...


# ---------- Test helper — no need to change anything below ----------
# run_test is a lambda (Java: () -> ...): a tiny function that calls YOUR
# function. check() calls it inside try, so an error in unfinished code
# prints FAIL instead of stopping the whole file.
_count = 0  # how many checks ran so far: gives each result a number


def check(label: str, run_test: Callable[[], object], expected: object) -> None:
    global _count  # change the module variable above. Java: a static field
    _count += 1
    try:
        actual = run_test()  # call the lambda now -> what your code returned
        if actual == expected:
            result = "PASS"
        else:  # {actual!r} = value in code form, e.g. 'abc' with quotes
            result = f"FAIL (got {actual!r}, expected {expected!r})"
    except Exception as error:  # Java: catch (Exception error)
        # Traceback = the call chain (Java: stack trace). Keep only frames in
        # this file, so the line shown is in YOUR code, not inside a library.
        mine = [f for f in traceback.extract_tb(error.__traceback__)
                if f.filename == __file__]
        where = f"\n{'':<21}line {mine[-1].lineno}: {mine[-1].line}" if mine else ""
        result = f"FAIL ({type(error).__name__}: {error}){where}"
    print(f"{_count:>2}. {label:<16} {result}")  # :>2 = right-align, :<16 = pad


def _save_then_load(path: Path, data: Any) -> Any:
    """Test helper: save, then load back (a lambda can hold only one expression)."""
    save_json(path, data)
    return load_json(path)


def _report_size(path: Path, name: str) -> Any:
    save_report(path)
    return load_json(path).get(name)


if __name__ == "__main__":
    # All test files go into a temp folder, deleted at the end.
    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        sample = {"model": "qwen3:4b", "tags": ["a", "b"], "gpu": None}
        check("json round", lambda: _save_then_load(temp / "s.json", sample), sample)
        check("json pretty", lambda: (temp / "s.json").read_text(encoding="utf-8")
              .startswith('{\n  "model"'), True)
        (temp / "n.txt").write_text("a\n\n   \nb\n", encoding="utf-8")
        check("count lines", lambda: count_lines(temp / "n.txt"), 2)
        check("version", lambda: ollama_version().count("."), 2)
        check("names has 4b", lambda: "qwen3:4b" in model_names(), True)
        check("names sorted", lambda: model_names() == sorted(model_names()), True)
        check("size 4b", lambda: model_size_gb("qwen3:4b"), 2.5)
        check("size missing", lambda: model_size_gb("no-such-model"), None)
        check("installed yes", lambda: is_installed("qwen3:4b"), True)
        check("installed no", lambda: is_installed("no-such-model"), False)
        check("context 4b", lambda: context_length("qwen3:4b"), 262144)
        check("report", lambda: _report_size(temp / "r.json", "qwen3:4b"), 2.5)
