"""Part 1 of 4: how an LLM sees text — tokens and token ids.

Pure Python, no model yet (Ollama comes in 2.2). Run it, then read each block.
How to read: code between "explicit start/end" is the long, step-by-step way.
The "# concise:" line right after it does the same in short Python style.
"""

# One small text we reuse in every example. Spaces separate the words,
# and "." is a word too, so the sentence end is visible.
SAMPLE_TEXT = "the cat sat on the mat . the cat ate the rat ."


# ---------- 1a. Two ways to cut text into tokens ----------
# A model never sees letters. It sees integer ids, one id per token.
# First we must decide what one "token" is. Two simple choices:

# Choice 1: one token per character.
# list("cat sat") walks the string and puts each character in a list.
# char_tokens = ['c', 'a', 't', ' ', 's', 'a', 't']
# Good: very few different tokens. Bad: a long text = a very long list.
char_tokens = list("cat sat")

# Choice 2: one token per word.
# split() with no argument cuts the string at every space.
# word_tokens = ['the', 'cat', 'sat', 'on', 'the', 'mat', '.', ...]
# Good: short lists. Bad: millions of possible words, and a new word
# the model never saw has no id at all.
word_tokens = SAMPLE_TEXT.split()

print("chars:", char_tokens)
print("words:", word_tokens[:6], "...")  # [:6] = first 6 items. Java: subList(0, 6)


# ---------- 1b. Vocabulary: every known token gets one id ----------
# The vocabulary is a map from token to id. Java: Map<String, Integer>.
# Steps: drop duplicate words, sort them (so ids are always the same),
# then number them 0, 1, 2, ...
# --- explicit start ---
# set(...) keeps each word once; sorted(...) turns it into a sorted list.
# unique_words = ['.', 'ate', 'cat', 'mat', 'on', 'rat', 'sat', 'the']
unique_words = sorted(set(word_tokens))

# word_to_id = {'.': 0, 'ate': 1, 'cat': 2, ...}  <- this IS the vocabulary
word_to_id: dict[str, int] = {}  # keys are str, values are int
for word_id in range(len(unique_words)):  # word_id = 0, 1, 2, ... 7
    word = unique_words[word_id]
    word_to_id[word] = word_id
# --- explicit end ---
# concise: word_to_id = {word: word_id for word_id, word in enumerate(unique_words)}
#          enumerate gives (index, item) pairs; {key: value for ...} builds a dict


# ---------- 1c. Encode: text -> list of ids ----------
# This list of numbers is what the model really receives.
# token_ids = [7, 2, 6, 4, 7, 3, 0, ...]   ('the' -> 7, 'cat' -> 2, ...)
# --- explicit start ---
token_ids: list[int] = []  # ': list[int]' = what goes in. Java: List<Integer>
for word in word_tokens:
    token_ids.append(word_to_id[word])  # look the word up, keep its id
# --- explicit end ---
# concise: token_ids = [word_to_id[word] for word in word_tokens]

print("vocab:", word_to_id)
print("ids:  ", token_ids)
