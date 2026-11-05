"""Debug logging for every lesson file: ONE logger, toggle per function.

Use:
    from lab_tools.log import debug, log

    @debug                      # add = this function's log.debug lines print
    def my_func(x: int) -> int:  # remove @debug = silent
        log.debug("x=%s", x)    # %s = filled with x, only if it prints
        return x

Every line starts with the function name, e.g.  my_func   x=5
"""

import logging
from collections.abc import Callable

DEBUG_ON: set[str] = set()  # names of functions marked @debug

logging.basicConfig(format="%(funcName)-18s %(message)s")
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
