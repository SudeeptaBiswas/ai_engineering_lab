"""Part 1 of 2: modules and imports. No network.

Uses prompts_1_5.py, the file next to this one. Run from the repo root:
    uv run python 01_python_fundamentals/1_5_modules_exceptions/examples_1_5_1_modules.py
"""

import sys  # the running Python itself. Java: System, plus the classpath
from pathlib import Path

# ---------- 1. Import runs the file, once ----------
print("1. first import:")
import prompts_1_5  # runs prompts_1_5.py top to bottom -> its print shows

print("   second import (no print: already loaded):")
import prompts_1_5 as again  # `as` = a second name for the same module

# `is` = the same object in memory. Java: ==  on references
print("   same module object:", again is prompts_1_5)
# sys.modules = every loaded module, by name. Java: classes in the ClassLoader
print("   in sys.modules:", "prompts_1_5" in sys.modules)

# ---------- 2. Three ways to import ----------
# a) import module  -> write module.name. Java: fully qualified name
print("\n2a.", prompts_1_5.SYSTEM_PROMPT)

# b) from module import name -> use the name alone. Java: import static
from prompts_1_5 import build_messages

print("2b.", build_messages("  Name a colour. "))

# c) import module as short_name. You will see `import numpy as np` in 4.1.
import prompts_1_5 as prompts

print("2c.", prompts.build_messages("Name a fruit.")[1])
# Never: `from module import *` (pulls in every name; you can't tell where
# a name came from). Java has the same warning for import x.*

# ---------- 3. __name__: who is running? ----------
# Run directly -> "__main__". Imported -> the module's own name.
print("\n3. here:", repr(__name__), "| there:", repr(prompts_1_5.__name__))
# That's why every exercises file ends with: if __name__ == "__main__":
# The checks run when you run the file, not when another file imports it.

# ---------- 4. Where Python looks (Java: the classpath) ----------
# sys.path = folders searched, in order. [0] = the folder of the file you ran.
# That is why `import prompts_1_5` works: it sits next to this file.
print("\n4. sys.path[0]:", Path(sys.path[0]).name)
import lab_tools  # found in .venv: `uv sync` installed it (pyproject.toml)

print("   lab_tools is a package (folder + __init__.py):",
      Path(lab_tools.__file__).name)
# A folder name must be a valid name to import it: no digit first, no "-".
# So `import 01_python_fundamentals` is a SyntaxError.
print("   '01_python_fundamentals' importable name?",
      "01_python_fundamentals".isidentifier())
print("   'lab_tools' importable name?", "lab_tools".isidentifier())

# ---------- 5. "Private" is only a hint ----------
# Python runs this fine. Pyright (strict) reports it, so we silence it here.
print("\n5. _clean still callable:",
      repr(prompts_1_5._clean("  hi  ")))  # pyright: ignore[reportPrivateUsage]
