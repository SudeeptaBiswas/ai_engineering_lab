"""Test helper for every exercises file: numbered PASS / FAIL lines.

Use:
    from lab_tools.check import check

    check("add", lambda: add(2, 3), 5)   # lambda = YOUR call, run later

On FAIL it prints "path:line" links. Ctrl+click one in the VS Code terminal
to jump to the test line, or to the line in your code that raised the error.
"""

import inspect  # find the line that called check()
import traceback  # find the line that raised an error
from collections.abc import Callable  # type of a function
from pathlib import Path

_count = 0  # how many checks ran so far: gives each result a number
_PAD = " " * 21  # lines the extra info up under the label


def _link(file: str, line: int | None) -> str:
    """'path:line', path from the folder you run in (full path if other drive)."""
    try:
        path = Path(file).relative_to(Path.cwd(), walk_up=True)
    except ValueError:  # run from another drive: no relative path exists
        path = Path(file)
    return f"{path}:{line}"


# run_test is a lambda (Java: () -> ...): a tiny function that calls YOUR
# function. check() calls it inside try, so an error in unfinished code
# prints FAIL instead of stopping the whole file.
# Callable[[], object] = takes nothing, returns anything. Java: Supplier<Object>
def check(label: str, run_test: Callable[[], object], expected: object) -> None:
    global _count  # change the module variable above. Java: a static field
    _count += 1
    caller = inspect.stack(0)[1]  # [1] = who called check(): the test line
    try:
        actual = run_test()  # call the lambda now -> what your code returned
        if actual == expected:
            result = "PASS"
        else:  # {actual!r} = value in code form, e.g. 'abc' with quotes
            result = f"FAIL (got {actual!r}, expected {expected!r})"
    except Exception as error:  # Java: catch (Exception error)
        result = f"FAIL ({type(error).__name__}: {error})"
        # Traceback = the call chain (Java: stack trace). Keep only frames in
        # the test's file, so the line shown is in YOUR code, not a library.
        mine = [f for f in traceback.extract_tb(error.__traceback__)
                if f.filename == caller.filename]
        if mine:
            link = _link(caller.filename, mine[-1].lineno)
            result += f"\n{_PAD}error {link}  {mine[-1].line}"
    if result != "PASS":
        result += f"\n{_PAD}test  {_link(caller.filename, caller.lineno)}"
    print(f"{_count:>2}. {label:<16} {result}")  # :>2 = right-align, :<16 = pad
