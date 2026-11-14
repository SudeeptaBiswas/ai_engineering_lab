"""Runs when you type `uv run python -m assistant` (from the repo root).

`python -m assistant` runs the package's __main__.py.
Add --debug to see the log: every step, with file:line and function name.
"""

import logging
import sys

from assistant.cli import main
from lab_tools.log import log

DEBUG_FLAG = "--debug"


def make_output_safe() -> None:
    """Stop a crash when the model prints a character the terminal can't show.

    Seen: an emoji on a cp932 terminal -> UnicodeEncodeError. errors="replace"
    prints "?" instead.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)  # None if stdout has no such method
    if reconfigure is not None:
        reconfigure(errors="replace")


def hide_log_unless_asked(command_line_arguments: list[str]) -> None:
    """Show the debug log only when --debug was typed, so the chat stays clean.

    Args:
        command_line_arguments: e.g. sys.argv[1:] = ["--debug"].
    """
    debug_asked = DEBUG_FLAG in command_line_arguments
    if not debug_asked:
        log.setLevel(logging.WARNING)  # debug lines are below WARNING, so they are hidden


make_output_safe()
hide_log_unless_asked(sys.argv[1:])
main()
