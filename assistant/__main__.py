"""Runs when you type `uv run python -m assistant` (from the repo root).

`python -m assistant` runs the package's __main__.py. Java: the class with
`public static void main` named in the jar's manifest.
"""

from assistant.cli import main

main()
