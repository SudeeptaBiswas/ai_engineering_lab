"""Runs when you type `uv run python -m assistant` (from the repo root).

`python -m assistant` runs the package's __main__.py. Java: the class with
`public static void main` named in the jar's manifest.
"""

import sys

from assistant.cli import main

# The model may print an emoji the terminal's encoding lacks (seen: cp932,
# UnicodeEncodeError). errors="replace" prints "?" instead of crashing.
reconfigure = getattr(sys.stdout, "reconfigure", None)  # None if stdout has no such method
if reconfigure is not None:
    reconfigure(errors="replace")

main()
