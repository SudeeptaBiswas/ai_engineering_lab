"""Runs the lesson-code rules (lesson_rules.py) on the right files.

Use:
    uv run python -m lab_tools.lesson_rules_run FILE...   # exit 1 if a rule breaks
    uv run python -m lab_tools.lesson_rules_run --all     # every file in scope
    uv run python -m lab_tools.lesson_rules_run --hook    # Claude Code PostToolUse
    uv run python -m lab_tools.lesson_rules_run --staged  # git pre-commit
Which files (DECISIONS 2026-11-15):
  examples_*.py before 4.1          -> rules 1-5 (blocks)
  examples_*.py from 04 on          -> rules 1-7 (blocks)
  other .py in assistant/, 2.6, 3.5 -> rules 3-7, no idiom rules (blocks)
    and every phase folder from 04 on
  same, with USER_CODE_MARK inside  -> same rules, WARN only (the user's code)
  LESSON_N_N.md from 4.1 on         -> section order (blocks)
Files in lesson_rules_legacy.txt are skipped (rewritten at course end).
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

from lab_tools.lesson_rules import check_lesson_md, check_source

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_LIST = Path(__file__).with_name("lesson_rules_legacy.txt")
CODE_FOLDERS = ("assistant/", "02_llm_fundamentals/2_6_assistant_v1/", "03_prompting_tools/3_5_assistant_v2/")
FIRST_CHECKED_PHASE = 4  # 04_rag and later: every .py follows CODE_STYLE
FIRST_CHECKED_LESSON_MD = (4, 1)  # CODE_STYLE section 12 starts at 4.1
USER_CODE_MARK = "# lesson-rules: user-code"  # in a stub file the user fills: warn, never block


def repo_path(path: Path) -> str:
    """Path from the repo root with / slashes, e.g. '02_x/examples_2_5_1.py'.

    Args:
        path: any file path; outside the repo it comes back whole.
    Returns:
        The path as text with / slashes.
    """
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:  # not inside the repo (e.g. a scratch file)
        return path.resolve().as_posix()


def legacy_files() -> set[str]:
    """Repo paths skipped until the course-end rewrite."""
    text = LEGACY_LIST.read_text(encoding="utf-8") if LEGACY_LIST.exists() else ""
    return {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}


def file_kind(relative: str) -> str | None:
    """Which rules a file gets: "old_example", "example", "code", "lesson_md", or None (not checked)."""
    name = relative.rsplit("/", 1)[-1]
    phase_match = re.match(r"(\d\d)_", relative)
    in_late_phase = phase_match is not None and int(phase_match.group(1)) >= FIRST_CHECKED_PHASE
    lesson_match = re.fullmatch(r"LESSON_(\d+)_(\d+)\.md", name)
    if lesson_match:
        topic = (int(lesson_match.group(1)), int(lesson_match.group(2)))
        return "lesson_md" if topic >= FIRST_CHECKED_LESSON_MD else None
    if not name.endswith(".py"):
        return None
    if name.startswith("examples_"):
        return "example" if in_late_phase else "old_example"
    if relative.startswith(CODE_FOLDERS) or in_late_phase:
        return "code"
    return None


def names_from_mode(arguments: list[str]) -> list[str]:
    """The file paths the mode points at."""
    if arguments == ["--hook"]:  # Claude Code sends JSON on stdin
        event = cast(dict[str, Any], json.load(sys.stdin))
        tool_input = cast(dict[str, Any], event.get("tool_input", {}))
        return [str(tool_input.get("file_path", ""))]
    if arguments == ["--staged"]:  # files in the commit being made
        git_output = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AMR"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
        return [str(REPO_ROOT / name) for name in git_output.splitlines()]
    if arguments == ["--all"]:
        tracked = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True,
                                 check=True).stdout
        return [str(REPO_ROOT / name) for name in tracked.splitlines()]
    return arguments


def files_to_check(arguments: list[str]) -> list[tuple[str, str, str]]:
    """(repo path, kind, source text) for each file in scope."""
    skipped = legacy_files()
    found: list[tuple[str, str, str]] = []
    for name in names_from_mode(arguments):
        path = Path(name)
        relative = repo_path(path)
        kind = file_kind(relative)
        if kind is None or not path.exists() or relative in skipped:
            continue
        if arguments == ["--staged"]:  # check what is staged, not the working copy
            source = subprocess.run(["git", "show", f":{relative}"], cwd=REPO_ROOT,
                                    capture_output=True, text=True, encoding="utf-8", check=True).stdout
        else:
            source = path.read_text(encoding="utf-8")
        found.append((relative, kind, source))
    return found


def main(arguments: list[str]) -> int:
    """Print every rule break. Returns 0 = all good, 1 = broken (2 in hook mode)."""
    blocking: list[str] = []
    warnings: list[str] = []
    for relative, kind, source in files_to_check(arguments):
        if kind == "lesson_md":
            problems = check_lesson_md(source)
        else:
            is_example = kind in ("example", "old_example")
            follows_code_style = kind in ("example", "code")
            problems = check_source(source, is_example, follows_code_style)
        report = warnings if USER_CODE_MARK in source else blocking
        for line_number, message in problems:
            report.append(f"  {relative}:{line_number}  {message}")
    if warnings:
        print("Style notes on your code (warning only, CODE_STYLE.md):", file=sys.stderr)
        print("\n".join(warnings), file=sys.stderr)
    if not blocking:
        return 0
    print("Lesson rules broken (CODE_STYLE.md):", file=sys.stderr)
    print("\n".join(blocking), file=sys.stderr)
    return 2 if arguments == ["--hook"] else 1  # 2 = Claude Code shows it to Claude


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
