"""Runs the lesson-code rules (lesson_rules.py) on the right files.

Use:
    uv run python -m lab_tools.lesson_rules_run FILE...   # exit 1 if a rule breaks
    uv run python -m lab_tools.lesson_rules_run --hook    # Claude Code PostToolUse
    uv run python -m lab_tools.lesson_rules_run --staged  # git pre-commit
Only examples_*.py files are checked. Files in lesson_rules_legacy.txt are
skipped (rewritten at course end).
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

from lab_tools.lesson_rules import check_source

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_LIST = Path(__file__).with_name("lesson_rules_legacy.txt")


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


def files_to_check(arguments: list[str]) -> list[tuple[str, str]]:
    """(repo path, source text) for each lesson file the mode points at."""
    if arguments == ["--hook"]:  # Claude Code sends JSON on stdin
        event = cast(dict[str, Any], json.load(sys.stdin))
        tool_input = cast(dict[str, Any], event.get("tool_input", {}))
        names = [str(tool_input.get("file_path", ""))]
    elif arguments == ["--staged"]:  # files in the commit being made
        git_output = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AMR"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
        names = [str(REPO_ROOT / name) for name in git_output.splitlines()]
    else:
        names = arguments
    skipped = legacy_files()
    found: list[tuple[str, str]] = []
    for name in names:
        path = Path(name)
        if not (path.name.startswith("examples_") and path.suffix == ".py" and path.exists()):
            continue
        relative = repo_path(path)
        if relative in skipped:
            continue
        if arguments == ["--staged"]:  # check what is staged, not the working copy
            source = subprocess.run(["git", "show", f":{relative}"], cwd=REPO_ROOT,
                                    capture_output=True, text=True, encoding="utf-8", check=True).stdout
        else:
            source = path.read_text(encoding="utf-8")
        found.append((relative, source))
    return found


def main(arguments: list[str]) -> int:
    """Print every rule break. Returns 0 = all good, 1 = broken (2 in hook mode)."""
    report: list[str] = []
    for relative, source in files_to_check(arguments):
        for line_number, message in check_source(source):
            report.append(f"  {relative}:{line_number}  {message}")
    if not report:
        return 0
    print("Lesson rules broken (PLAN.md 'How we work'):", file=sys.stderr)
    print("\n".join(report), file=sys.stderr)
    return 2 if arguments == ["--hook"] else 1  # 2 = Claude Code shows it to Claude


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
