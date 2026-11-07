"""A tiny module for example part 1: chat helpers, like the ones 2.6 needs.

A module = one .py file. Its name = the file name without ".py".
Java: like one class file, but it can hold many functions and constants,
not only one class.
"""

# Top-level code runs ONCE, the first time someone imports this module.
# !r = show the value in code form, with quotes (1.7)
print(f"  [prompts_1_5 loading, __name__ = {__name__!r}]")

# A module constant. UPPER_CASE = "do not change". Java: public static final String
SYSTEM_PROMPT = "Reply with one word only."

Message = dict[str, str]  # {"role": ..., "content": ...} (lesson 2.3)


def _clean(text: str) -> str:
    """Leading _ = "private, for this module only". Only a hint: Python does
    not block it, but pyright (strict) flags use from outside. Java: private."""
    return text.strip()  # drop spaces and newlines at both ends


def build_messages(question: str) -> list[Message]:
    """System + user message, ready for POST /api/chat (lesson 2.3)."""
    system_message: Message = {"role": "system", "content": SYSTEM_PROMPT}
    user_message: Message = {"role": "user", "content": _clean(question)}
    return [system_message, user_message]


# True only when THIS file is run directly, not when it is imported.
# Java: public static void main(String[] args)
if __name__ == "__main__":
    print(build_messages("  Name a colour.  "))
