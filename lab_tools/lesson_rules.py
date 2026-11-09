"""Lesson-code rule check (PLAN.md "How we work", DECISIONS 2026-11-09).

Checks every examples_*.py file (lesson code Claude writes):
  1. no idioms in code (comprehension, lambda, ternary, zip, unpacking...):
     write the long way; the short form goes in a "# concise:" comment
  2. every "# --- explicit end ---" has a "# concise:" line right after
  3. no one-letter names ("_" is fine)
  4. every function has a docstring, with Args: (if it takes any) + Returns:
  5. at most 150 lines
A line with "# rule-ok: <reason>" skips rules 1 and 3 on that line
(e.g. a lesson whose topic IS comprehensions).
Run it with lesson_rules_run.py.
"""

import ast
from typing import cast

MAX_LINES = 150
EXPLICIT_END = "# --- explicit end ---"
RULE_OK = "# rule-ok:"
IDIOM_NODES: dict[type[ast.AST], str] = {
    ast.ListComp: "list comprehension", ast.SetComp: "set comprehension",
    ast.DictComp: "dict comprehension", ast.GeneratorExp: "generator expression",
    ast.Lambda: "lambda", ast.IfExp: "ternary (a if c else b)",
}
IDIOM_CALLS = {"zip", "enumerate", "map", "filter", "most_common"}


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


def check_source(source: str) -> list[tuple[int, str]]:
    """All rule breaks in one file's text, as (line number, message)."""
    lines = source.splitlines()
    problems: list[tuple[int, str]] = []
    if len(lines) > MAX_LINES:
        problems.append((1, f"{len(lines)} lines, max {MAX_LINES}: split the file"))
    for index, line in enumerate(lines):
        if line.strip() != EXPLICIT_END:
            continue
        following = [text.strip() for text in lines[index + 1:] if text.strip()]
        if not following or not following[0].startswith("# concise:"):
            problems.append((index + 1, "explicit block has no '# concise:' line after it"))
    for node in ast.walk(ast.parse(source)):
        line_number = cast(int, getattr(node, "lineno", 0))
        allowed = line_number > 0 and RULE_OK in lines[line_number - 1]
        idiom = idiom_in(node)
        if idiom and not allowed:
            problems.append((line_number, f"{idiom}: write it the long way, short form in '# concise:'"))
        short_name = short_name_in(node)
        if short_name and not allowed:
            problems.append((line_number, f"one-letter name '{short_name}': use a full name"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            problem = docstring_problem(node)
            if problem:
                problems.append((line_number, f"{node.name}(): {problem}"))
    return sorted(problems)
