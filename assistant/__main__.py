"""Runs when you type `uv run python -m assistant` (from the repo root).

`python -m assistant` runs the package's __main__.py.
Add --debug to see the log: every step, with file:line and function name.
"""

import logging
import sys

from assistant.cli import main
from lab_tools.log import debug, log

DEBUG_FLAG = "--debug"


@debug
def hide_log_unless_asked(command_line_arguments: list[str]) -> None:
    """Show the debug log only when --debug was typed, so the chat stays clean.

    Runs first: every log line after it follows this choice.
    Args:
        command_line_arguments: e.g. sys.argv[1:] = ["--debug"].
    """
    debug_asked = DEBUG_FLAG in command_line_arguments
    if not debug_asked:
        log.setLevel(logging.WARNING)  # debug lines are below WARNING, so they are hidden
    log.debug("result: debug log on (%s)", command_line_arguments)  # prints only when debug_asked


@debug
def make_output_safe() -> None:
    """Stop a crash when the model prints a character the terminal can't show.

    Seen: an emoji on a cp932 terminal -> UnicodeEncodeError. errors="replace"
    prints "?" instead.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)  # None if stdout has no such method
    has_reconfigure = reconfigure is not None
    if has_reconfigure:
        reconfigure(errors="replace")
    log.debug("result: has_reconfigure=%s", has_reconfigure)


hide_log_unless_asked(sys.argv[1:])
make_output_safe()
main()
