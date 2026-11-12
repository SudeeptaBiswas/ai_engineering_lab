"""Check: every folder with pytest tests is in VS Code's pytestArgs.

VS Code's Testing panel only looks in the folders listed in
.vscode/settings.json "python.testing.pytestArgs" (older lesson files run
code on import, so it can't scan the whole repo). A new pytest folder
missing from that list = tests silently not shown (DECISIONS 2026-11-12).

Use:
    uv run python -m lab_tools.vscode_tests   # exit 1 if a folder is missing
Runs in the git pre-commit hook (.githooks/pre-commit).
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parent.parent
SETTINGS = REPO_ROOT / ".vscode" / "settings.json"
TEST_FILE = re.compile(r"(test|examples|exercises)_.*\.py")  # pyproject python_files
USES_PYTEST = re.compile(r"^(import pytest|from pytest|def test_)", re.MULTILINE)


def pytest_folders() -> set[str]:
    """Folders (repo paths, / slashes) holding at least one pytest-style file.

    Returns:
        e.g. {"03_prompting_tools/3_1_prompt_patterns"}. Uses git's file list
        (committed + staged), so .venv and scratch files are skipped.
    """
    git_output = subprocess.run(["git", "ls-files", "*.py"], cwd=REPO_ROOT,
                                capture_output=True, text=True, check=True).stdout
    folders: set[str] = set()
    for name in git_output.splitlines():
        path = REPO_ROOT / name
        if not TEST_FILE.fullmatch(path.name) or not path.exists():
            continue
        if USES_PYTEST.search(path.read_text(encoding="utf-8")):
            folders.add(Path(name).parent.as_posix())
    return folders


def listed_folders() -> set[str]:
    """Folders in .vscode/settings.json pytestArgs (empty set if no file).

    Returns:
        The folder entries, with / slashes and no trailing slash.
    """
    if not SETTINGS.exists():
        return set()
    settings = cast(dict[str, Any], json.loads(SETTINGS.read_text(encoding="utf-8")))
    arguments = cast(list[str], settings.get("python.testing.pytestArgs", []))
    folders: set[str] = set()
    for argument in arguments:
        if not argument.startswith("-"):  # skip flags like -v
            folders.add(argument.replace("\\", "/").rstrip("/"))
    return folders


def main() -> int:
    """Print folders missing from pytestArgs.

    Returns:
        0 = all listed, 1 = something missing.
    """
    missing = sorted(pytest_folders() - listed_folders())
    if not missing:
        return 0
    print("VS Code won't show these tests. Add to .vscode/settings.json",
          "\"python.testing.pytestArgs\":", file=sys.stderr)
    for folder in missing:
        print(f"  \"{folder}\"", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
