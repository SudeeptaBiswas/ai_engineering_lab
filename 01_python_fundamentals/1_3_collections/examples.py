"""Python collections next to Java. Run it, then read each block."""

# import = Java import. `collections` is part of Python's standard library.
from collections import Counter, defaultdict

# ---------- list — like ArrayList ----------
models = ["qwen3", "llama3.2", "gemma3"]  # Java: new ArrayList<>(List.of(...))
models.append("phi4")  # Java: list.add("phi4")
models.insert(0, "mistral")  # Java: list.add(0, "mistral")
print("list:", models, "len =", len(models))  # len() works on every collection
print("first/last:", models[0], models[-1])  # -1 = last item, -2 = second last
print("slice [1:3]:", models[1:3])  # items 1 and 2 (end index excluded)
print("contains:", "qwen3" in models)  # Java: list.contains("qwen3")

# ---------- dict — like HashMap, but keeps insertion order ----------
sizes = {"qwen3": 4, "llama3.2": 3}  # Java: Map.of("qwen3", 4, ...)
sizes["gemma3"] = 4  # Java: map.put("gemma3", 4)
print("dict:", sizes)
# .get() returns None if the key is missing; 2nd arg = default (getOrDefault)
print("get missing:", sizes.get("phi4"), sizes.get("phi4", 0))
# .items() gives (key, value) pairs — like map.entrySet()
for name, size in sizes.items():
    print(f"  {name} -> {size}B")

# ---------- set — like HashSet ----------
tags = {"rag", "agent", "rag"}  # duplicate "rag" is dropped
print("set:", tags)
# | = union (addAll), & = intersection (retainAll)
print("union/intersection:", tags | {"mcp"}, tags & {"rag", "mcp"})

# ---------- tuple — fixed and immutable ----------
point = (3, 4)
x, y = point  # "unpacking": x = point[0], y = point[1]
print("tuple:", point, x, y)

# ---------- Comprehensions — a stream in one line ----------
nums = list(range(10))  # [0, 1, ..., 9]
# Pattern: [EXPRESSION for ITEM in LIST if CONDITION]
# Java: nums.stream().filter(n -> n % 2 == 0).map(n -> n * n).toList()
print("squares of evens:", [n * n for n in nums if n % 2 == 0])
# Dict version: {KEY: VALUE for ITEM in LIST}
print("word lengths:", {w: len(w) for w in models})
# Set version: {EXPRESSION for ITEM in LIST}
print("unique lower:", {t.lower() for t in ["RAG", "rag", "Mcp"]})

# ---------- Sorting with a key (like Comparator) ----------
scores = {"doc1": 0.42, "doc2": 0.91, "doc3": 0.77}
# lambda k: scores[k]  ==  Java: k -> scores.get(k)
# sorted() over a dict sorts its keys; key= says "compare by this value"
ranked = sorted(scores, key=lambda k: scores[k], reverse=True)
print("ranked:", ranked)
# kv is a (key, value) tuple, so kv[1] is the score
print("top pair:", max(scores.items(), key=lambda kv: kv[1]))

# ---------- zip and enumerate ----------
# zip pairs two lists item by item: ("a", 0.1), ("b", 0.2)
# enumerate adds a counter; start=1 makes it count from 1
for i, (name, score) in enumerate(zip(["a", "b"], [0.1, 0.2]), start=1):
    print(f"  {i}. {name}={score}")

# ---------- Counter and defaultdict ----------
words = "the cat and the hat and the bat".split()  # split on spaces -> list
# Counter counts items for you; most_common(2) = top 2
print("counter:", Counter(words).most_common(2))
# defaultdict(list): a missing key starts as [] automatically
# Java: map.computeIfAbsent(key, k -> new ArrayList<>()).add(w)
by_letter = defaultdict(list)
for w in words:
    by_letter[w[0]].append(w)  # w[0] = first letter of the word
print("grouped:", dict(by_letter))

# ---------- any / all — Java: stream().anyMatch / allMatch ----------
print("any > 0.9:", any(s > 0.9 for s in scores.values()))
print("all > 0.4:", all(s > 0.4 for s in scores.values()))
