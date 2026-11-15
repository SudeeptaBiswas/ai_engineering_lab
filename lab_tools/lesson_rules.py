"""Lesson-code rule check (PLAN.md "How we work", DECISIONS 2026-11-09).

Checks code Claude writes (which files: lesson_rules_run.py):
  1. no idioms in code (comprehension, lambda, ternary, zip, unpacking...):
     write the long way; the short form goes in a "# concise:" comment
  2. every "# --- explicit end ---" has a "# concise:" line right after
  3. no one-letter names ("_" is fine)
  4. every function has a docstring, with Args: (if it takes any) + Returns:
  5. at most 250 lines (aim under 150; CODE_STYLE.md section 11)
  6. every function has @debug and a log.debug line (CODE_STYLE rule 9)
  7. no test docstring starts with "Checks" (CODE_STYLE rule 10)
Rules 1-2 only for examples_*.py. A line with "# rule-ok: <reason>" skips
rules 1 and 3 on that line (e.g. a lesson whose topic IS comprehensions).
LESSON md files from 4.1 on: the sections of CODE_STYLE section 12, in order.
Run it with lesson_rules_run.py.
"""

import ast
from typing import cast

MAX_LINES = 250
EXPLICIT_END = "# --- explicit end ---"
RULE_OK = "# rule-ok:"
IDIOM_NODES: dict[type[ast.AST], str] = {
    ast.ListComp: "list comprehension", ast.SetComp: "set comprehension",
    ast.DictComp: "dict comprehension", ast.GeneratorExp: "generator expression",
    ast.Lambda: "lambda", ast.IfExp: "ternary (a if c else b)",
}
IDIOM_CALLS = {"zip", "enumerate", "map", "filter", "most_common"}
LOG_EXEMPT_MARK = "No own log lines"  # in a docstring: a per-item loop helper (CODE_STYLE rule 9)
LESSON_MD_HEADINGS = ("## The problem", "## Goal", "## How we get there", "## Steps", "## Your path",
                      "## Exercises")


def idiom_in(node: ast.AST) -> str | None:
    """Name of the idiom this node is, or None. e.g. ast.Lambda -> 'lambda'."""
    for node_type, idiom in IDIOM_NODES.items():
        if isinstance(node, node_type):
            return idiom
    if isinstance(node, ast.Call):
        called = ""
        if isinstance(node.func, ast.Name):
            called = node.func.id  # zip(...)
        elif isinstance(node.func, ast.Attribute):
            called = node.func.attr  # counter.most_common(...)
        if called in IDIOM_CALLS:
            return f"{called}()"
    if isinstance(node, ast.Tuple) and isinstance(node.ctx, ast.Store):
        return "unpacking (a, b = ...)"
    return None


def short_name_in(node: ast.AST) -> str | None:
    """A one-letter name this node creates (variable or parameter), or None."""
    name = ""
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
        name = node.id
    elif isinstance(node, ast.arg):
        name = node.arg
    if len(name) == 1 and name != "_":
        return name
    return None


def docstring_problem(function: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """What is missing from this function's docstring, or None if complete."""
    docstring = ast.get_docstring(function)
    if docstring is None:
        return "no docstring"
    all_args = function.args.posonlyargs + function.args.args + function.args.kwonlyargs
    takes_args = any(arg.arg not in ("self", "cls") for arg in all_args)
    if takes_args and "Args:" not in docstring:
        return "docstring has no Args:"
    returns_none = isinstance(function.returns, ast.Constant) and function.returns.value is None
    if function.returns is not None and not returns_none and "Returns:" not in docstring:
        return "docstring has no Returns:"
    return None


def is_stub(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True if the body is only a docstring + `raise NotImplementedError` (the user fills it)."""
    body = function.body
    if ast.get_docstring(function) is not None:
        body = body[1:]  # skip the docstring
    if len(body) != 1 or not isinstance(body[0], ast.Raise):
        return False
    raised = body[0].exc
    if isinstance(raised, ast.Call):  # NotImplementedError("...")
        raised = raised.func
    return isinstance(raised, ast.Name) and raised.id == "NotImplementedError"


def is_log_debug_call(node: ast.AST) -> bool:
    """True for a `log.debug(...)` call."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
        return False
    called_on = node.func.value
    return node.func.attr == "debug" and isinstance(called_on, ast.Name) and called_on.id == "log"


def logging_problem(function: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """What rule 9 misses here (@debug + at least one log.debug line), or None."""
    docstring = ast.get_docstring(function) or ""
    if function.name == "__init__" or is_stub(function) or LOG_EXEMPT_MARK in docstring:
        return None
    has_debug = any(isinstance(decorator, ast.Name) and decorator.id == "debug"
                    for decorator in function.decorator_list)
    if not has_debug:
        return f"no @debug (CODE_STYLE rule 9; a per-item loop helper says '{LOG_EXEMPT_MARK}')"
    if not any(is_log_debug_call(node) for node in ast.walk(function)):
        return "@debug but no log.debug line (CODE_STYLE rule 9)"
    return None


def test_docstring_problem(function: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """A test docstring that starts with "Checks" (rule 10: say what + why), or None."""
    docstring = ast.get_docstring(function) or ""
    if function.name.startswith("test_") and docstring.startswith("Checks"):
        return 'docstring starts with "Checks": say what we check and why (CODE_STYLE rule 10)'
    return None


def check_source(source: str, is_example: bool = True, follows_code_style: bool = False) -> list[tuple[int, str]]:
    """All rule breaks in one file's text, as (line number, message).

    is_example: rules 1-2 (idioms, '# concise:') apply.
    follows_code_style: rules 6-7 apply (files from 4.1 on, assistant/, its tests).
    """
    lines = source.splitlines()
    problems: list[tuple[int, str]] = []
    if len(lines) > MAX_LINES:
        problems.append((1, f"{len(lines)} lines, max {MAX_LINES}: split the file"))
    for index, line in enumerate(lines):
        if not is_example or line.strip() != EXPLICIT_END:
            continue
        following = [text.strip() for text in lines[index + 1:] if text.strip()]
        if not following or not following[0].startswith("# concise:"):
            problems.append((index + 1, "explicit block has no '# concise:' line after it"))
    for node in ast.walk(ast.parse(source)):
        line_number = cast(int, getattr(node, "lineno", 0))
        allowed = line_number > 0 and RULE_OK in lines[line_number - 1]
        idiom = idiom_in(node)
        if is_example and idiom and not allowed:
            problems.append((line_number, f"{idiom}: write it the long way, short form in '# concise:'"))
        short_name = short_name_in(node)
        if short_name and not allowed:
            problems.append((line_number, f"one-letter name '{short_name}': use a full name"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_problems = [docstring_problem(node)]
            if follows_code_style:
                function_problems += [logging_problem(node), test_docstring_problem(node)]
            for problem in function_problems:
                if problem:
                    problems.append((line_number, f"{node.name}(): {problem}"))
    return sorted(problems)


def check_lesson_md(text: str) -> list[tuple[int, str]]:
    """Missing or out-of-order sections in a LESSON md (CODE_STYLE section 12)."""
    lines = text.splitlines()
    problems: list[tuple[int, str]] = []
    previous_index = -1
    for heading in LESSON_MD_HEADINGS:
        found_index = next((index for index, line in enumerate(lines) if line.startswith(heading)), None)
        if found_index is None:
            problems.append((1, f"missing section '{heading}' (CODE_STYLE section 12)"))
            continue
        if found_index < previous_index:
            problems.append((found_index + 1, f"'{heading}' is out of order (CODE_STYLE section 12)"))
        previous_index = found_index
    return problems
