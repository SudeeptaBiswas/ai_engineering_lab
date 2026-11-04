"""Part 3 of 4: next-token guessing and softmax.

Same reading rule: code between "explicit start/end" is the long way;
the "# concise:" line right after it is the short Python way.
"""

import math  # math.exp, math.ceil. Java: Math.exp, Math.ceil

SAMPLE_TEXT = "the cat sat on the mat . the cat ate the rat ."
word_tokens = SAMPLE_TEXT.split()  # ['the', 'cat', 'sat', ...]


# ---------- 3. Next-token prediction ----------
# A real LLM: tokens so far -> a score for every token in the vocabulary.
# Toy version: count which word comes right after which word.
# next_word_counts = {'the': {'cat': 2, 'mat': 1, 'rat': 1}, 'cat': {...}, ...}
#   read as: after 'the' we saw 'cat' 2 times, 'mat' 1 time, 'rat' 1 time.
# Java: Map<String, Map<String, Integer>>
# --- explicit start ---
next_word_counts: dict[str, dict[str, int]] = {}
for position in range(len(word_tokens) - 1):  # last word has no next word
    current_word = word_tokens[position]
    next_word = word_tokens[position + 1]
    if current_word not in next_word_counts:
        next_word_counts[current_word] = {}  # first time: empty inner map
    if next_word not in next_word_counts[current_word]:
        next_word_counts[current_word][next_word] = 0
    next_word_counts[current_word][next_word] += 1
# --- explicit end ---
# concise: next_word_counts: dict[str, Counter] = {}
#          for current_word, next_word in zip(word_tokens, word_tokens[1:]):
#              next_word_counts.setdefault(current_word, Counter())[next_word] += 1
#          setdefault = Java computeIfAbsent
print("after 'the':", next_word_counts["the"])


def most_frequent(word_to_count: dict[str, int]) -> str:
    """The word with the biggest count. A tie keeps the first one seen.

    {'cat': 2, 'mat': 1, 'rat': 1}  ->  'cat'
    """
    # --- explicit start ---
    best_word = ""  # empty start, replaced in the loop
    best_count = 0
    for word in word_to_count:
        if word_to_count[word] > best_count:
            best_word = word
            best_count = word_to_count[word]
    # --- explicit end ---
    # concise: return Counter(word_to_count).most_common(1)[0][0]
    return best_word


# Generate: take the most likely next word, add it, repeat. This loop is
# called "autoregressive" generation — the same loop a real LLM runs.
generated_words = ["the"]  # the start text (the "prompt")
for _ in range(5):  # 5 more words; _ = loop variable we don't use
    # --- explicit start ---
    last_word = generated_words[len(generated_words) - 1]
    # --- explicit end ---
    # concise: last_word = generated_words[-1]   (negative index counts from the end)
    generated_words.append(most_frequent(next_word_counts[last_word]))
# " ".join(list) = Java String.join(" ", list).
# Always taking the top word = "greedy" -> boring, repeats. Fix: sampling (2.4)
print("generated:", " ".join(generated_words))


# ---------- 4. Scores -> probabilities (softmax) ----------
# Real models output one raw score per token, called a "logit".
# Softmax turns scores into probabilities between 0 and 1 that add up to 1.
def softmax(logits: list[float]) -> list[float]:
    """[2.0, 1.0, 0.5]  ->  [0.63, 0.23, 0.14]  (rounded)"""
    # --- explicit start ---
    # Step 1: e^score. Every result is positive; a bigger score grows faster.
    exp_scores: list[float] = []
    for logit in logits:
        exp_scores.append(math.exp(logit))
    # Step 2: divide each by the total, so they add up to 1.
    exp_total = sum(exp_scores)
    probabilities: list[float] = []
    for exp_score in exp_scores:
        probabilities.append(exp_score / exp_total)
    # --- explicit end ---
    # concise: exp_scores = [math.exp(logit) for logit in logits]
    #          return [exp_score / sum(exp_scores) for exp_score in exp_scores]
    return probabilities


# word_to_logit: what a model might score for the word after "the".
word_to_logit = {"cat": 2.0, "mat": 1.0, "rat": 0.5}
# --- explicit start ---
candidate_words = list(word_to_logit.keys())  # ['cat', 'mat', 'rat']
candidate_probs = softmax(list(word_to_logit.values()))  # [0.63, 0.23, 0.14]
for index in range(len(candidate_words)):
    # :.2f = 2 decimals. Java: String.format("%.2f", x)
    print(f"  P({candidate_words[index]}) = {candidate_probs[index]:.2f}")
# --- explicit end ---
# concise: for word, prob in zip(word_to_logit, softmax(list(word_to_logit.values()))):
#              print(f"  P({word}) = {prob:.2f}")
#          zip pairs up two lists: ('cat', 0.63), ('mat', 0.23), ...
