# 1.1 Setup: uv, venv, project layout (~1 h)

## Java → Python map
| Java | Python (this repo) |
|---|---|
| Maven / Gradle | `uv` |
| `pom.xml` | `pyproject.toml` |
| Gradle lockfile | `uv.lock` (exact versions, commit it) |
| `~/.m2` shared repo | `.venv/` per project (git-ignored) |
| `java -version` / toolchain | `.python-version` (pinned to 3.13) |
| `mvn exec:java` | `uv run python file.py` |
| `<dependency>` | `uv add httpx` |
| test scope | `uv add --dev pytest` |

Key idea: each project gets its own isolated `.venv`. Packages never leak
between projects. `uv run` uses that `.venv` automatically. No "activate" needed.

## No `main` class needed
Python runs a file top to bottom. The `if __name__ == "__main__":` guard means
"only run this when the file is run directly, not when imported" —
like a `public static void main` that is skipped on import.

## Do it
1. Open a terminal in the repo root (VS Code: Ctrl+`).
2. Run: `uv run python 01_python_fundamentals/1_1_setup/hello.py`
3. Read [hello.py](hello.py). Change the name and run again.
4. Run `uv tree` — shows dependencies (empty for now).

## VS Code
- Install the "Python" extension (Microsoft) if missing.
- Ctrl+Shift+P → "Python: Select Interpreter" → pick `.venv`.

## Done when
- [ ] hello.py runs and prints your name.
- [ ] You can explain: pyproject.toml, uv.lock, .venv.
