"""Part 4 of 4: context window — and why old messages get dropped.

Same reading rule: code between "explicit start/end" is the long way;
the "# concise:" line right after it is the short Python way.

The model sees at most a fixed number of tokens per call: system message
+ chat history + new question + its own answer. It keeps NO memory between
calls, so your code resends the whole chat every time, and must drop old
messages once the chat is too long.
"""

import math  # math.ceil = round UP. Java: Math.ceil

# Pretend limit, kept tiny so we hit it. Real models: thousands to 1M+ tokens.
CONTEXT_WINDOW_TOKENS = 20

# The chat so far, oldest first. Each message is a dict with two keys:
#   "role":    who wrote it — "system" (rules), "user" (you), "assistant" (model)
#   "content": the text itself
# This is the exact shape real chat APIs (Ollama, OpenAI, Claude) use.
chat_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is a token?"},
    {"role": "assistant", "content": "A small piece of text, often part of a word."},
    {"role": "user", "content": "And a context window?"},
]


def count_tokens(messages: list[dict]) -> int:
    """Estimate tokens for all messages: ~4 characters = 1 token, round UP.

    "What is a token?" has 16 characters -> 16 / 4 = 4 tokens.
    """
    # --- explicit start ---
    total_tokens = 0
    for message in messages:
        characters = len(message["content"])
        total_tokens += math.ceil(characters / 4)  # 2.75 -> 3
    # --- explicit end ---
    # concise: return sum(math.ceil(len(message["content"]) / 4)
    #                      for message in messages)
    return total_tokens


print("tokens used:", count_tokens(chat_messages), "of", CONTEXT_WINDOW_TOKENS)

# Too big? Drop the OLDEST message after the system one, then check again.
# Index 0 is the system message (it holds the rules), so we always keep it.
# Index 1 is the oldest normal message, so that is the one we remove.
while count_tokens(chat_messages) > CONTEXT_WINDOW_TOKENS:
    dropped_message = chat_messages.pop(1)  # pop(1) removes AND returns item 1
    print("  dropped:", dropped_message["content"])

# Collect just the roles that are left, to show what survived.
# remaining_roles = ['system', 'user']
# --- explicit start ---
remaining_roles = []
for message in chat_messages:
    remaining_roles.append(message["role"])
# --- explicit end ---
# concise: remaining_roles = [message["role"] for message in chat_messages]
print("left:", remaining_roles)
