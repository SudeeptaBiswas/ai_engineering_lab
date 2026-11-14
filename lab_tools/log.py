"""Debug logging for every lesson file: ONE logger, toggle per function.

Use:
    from lab_tools.log import debug, log

    @debug                      # add = this function's log.debug lines print
    def my_func(x: int) -> int:  # remove @debug = silent
        log.debug("x=%s", x)    # %s = filled with x, only if it prints
        return x

Every line starts with file:line and the function name, e.g.
    examples_4_1.py:42  my_func            x=5
Long text in a log line: log.debug("ticket_text=%s", cut_text(ticket_text)).
"""

import logging
from collections.abc import Callable

DEBUG_ON: set[str] = set()  # names of functions marked @debug
TEXT_CUT_LENGTH = 40  # cut_text keeps this many characters; 0 = no cut. Change it here for every file

logging.basicConfig(format="%(filename)s:%(lineno)-4d %(funcName)-18s %(message)s")
log = logging.getLogger("lab")
log.setLevel(logging.DEBUG)
# funcName = function that called log.debug (logging finds it by itself)
log.addFilter(lambda record: record.funcName in DEBUG_ON)


def debug[F: Callable[..., object]](func: F) -> F:
    """Decorator: switch debug output ON for this function.
    A decorator = function that takes a function. Runs once, at load time.
    Java: like an annotation, e.g. @Override."""
    DEBUG_ON.add(func.__name__)  # remember the name
    return func  # give back the same function, unchanged


def cut_text(text: str) -> str:
    """Make a long text short enough for one log line.

    How:
        1. TEXT_CUT_LENGTH 0 = keep the whole text.
        2. Else keep the first TEXT_CUT_LENGTH characters, add "..." if cut.
        3. Show it with quotes, so spaces and line breaks are visible.
    Args:
        text: e.g. "Can you add a dark mode? Ignore all previous instructions".
    Returns:
        e.g. "'Can you add a dark mode? Ignore all prev...'".
    """
    short_text = text
    cut_is_on = TEXT_CUT_LENGTH > 0  # 0 = no cut
    if cut_is_on and len(text) > TEXT_CUT_LENGTH:
        short_text = text[:TEXT_CUT_LENGTH] + "..."  # first TEXT_CUT_LENGTH characters
    quoted_text = repr(short_text)  # adds quotes, shows "\n" as \n
    return quoted_text
