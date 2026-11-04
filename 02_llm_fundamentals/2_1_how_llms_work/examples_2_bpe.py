"""Part 2 of 4: BPE — how real tokenizers pick sub-word pieces.

Same reading rule: code between "explicit start/end" is the long way;
the "# concise:" line right after it is the short Python way.

Idea: start with single characters. Find the two neighbours that appear
together most often, glue them into one token. Repeat.
Real tokenizers do tens of thousands of merges on huge text; we do 4.
"""


def count_pairs(tokens: list[str]) -> dict[tuple[str, str], int]:
    """Count every pair of neighbour tokens.

    tokens        = ['t', 'h', 'e', ' ', 'c', 'a', 't']
    pair_to_count = {('t', 'h'): 1, ('h', 'e'): 1, ('e', ' '): 1, ...}
    """
    # --- explicit start ---
    pair_to_count: dict[tuple[str, str], int] = {}
    # Stop one early: the last token has no right-hand neighbour.
    for position in range(len(tokens) - 1):
        # A tuple (left, right) can be a dict key. Java: a small record.
        neighbour_pair = (tokens[position], tokens[position + 1])
        if neighbour_pair not in pair_to_count:
            pair_to_count[neighbour_pair] = 0  # first time we see this pair
        pair_to_count[neighbour_pair] += 1
    # --- explicit end ---
    # concise: return Counter(zip(tokens, tokens[1:]))
    #          zip(a, a[1:]) walks neighbours; Counter (collections) counts them
    return pair_to_count


def merge_pair(tokens: list[str], pair_to_merge: tuple[str, str]) -> list[str]:
    """Glue every place where `pair_to_merge` appears into one token.

    tokens = ['c', 'a', 't'], pair_to_merge = ('a', 't')  ->  ['c', 'at']
    """
    # --- explicit start ---
    merged_tokens: list[str] = []  # the new, shorter list we build
    position = 0  # index of the token we look at now
    # --- explicit end ---
    # concise: merged_tokens, position = [], 0   (two assignments in one line)
    while position < len(tokens):
        has_right_neighbour = position + 1 < len(tokens)
        if (
            has_right_neighbour
            and (tokens[position], tokens[position + 1]) == pair_to_merge
        ):
            glued_token = tokens[position] + tokens[position + 1]  # 'a' + 't' = 'at'
            merged_tokens.append(glued_token)
            position += 2  # both halves are used up, jump over them
        else:
            merged_tokens.append(tokens[position])  # keep this token as it is
            position += 1
    return merged_tokens


# Start: one token per character. Spaces are tokens too.
# bpe_tokens = ['t', 'h', 'e', ' ', 'c', 'a', 't', ...]  (22 tokens)
bpe_tokens = list("the cat sat on the mat")

for merge_number in range(1, 5):  # 1, 2, 3, 4  (5 is not included)
    pair_to_count = count_pairs(bpe_tokens)

    # Find the pair with the biggest count. A tie keeps the first one seen.
    # --- explicit start ---
    best_pair = ("", "")  # empty start; e.g. ('a', 't') after the loop
    best_pair_count = 0  # e.g. 3  (how often best_pair appears)
    for neighbour_pair in pair_to_count:  # a dict keeps insertion order
        if pair_to_count[neighbour_pair] > best_pair_count:
            best_pair = neighbour_pair
            best_pair_count = pair_to_count[neighbour_pair]
    # --- explicit end ---
    # concise: best_pair = Counter(...).most_common(1)[0][0]
    #          most_common(1) -> [(pair, count)]; [0][0] takes the pair

    bpe_tokens = merge_pair(bpe_tokens, best_pair)  # list gets shorter each time
    # !r = show in code form (with quotes); :12 = pad to 12 chars
    print(f"merge {merge_number}: {best_pair!r:12} -> {len(bpe_tokens)} tokens")

print("after BPE:", bpe_tokens)
