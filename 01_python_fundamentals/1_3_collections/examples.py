"""Python collections next to Java. Run it, then read each block."""

from collections import Counter, defaultdict

# list — like ArrayList
models = ["qwen3", "llama3.2", "gemma3"]
models.append("phi4")
models.insert(0, "mistral")
print("list:", models, "len =", len(models))
print("first/last:", models[0], models[-1])
print("slice [1:3]:", models[1:3])
print("contains:", "qwen3" in models)

# dict — like HashMap, but keeps insertion order
sizes = {"qwen3": 4, "llama3.2": 3}
sizes["gemma3"] = 4
print("dict:", sizes)
print("get missing:", sizes.get("phi4"), sizes.get("phi4", 0))
for name, size in sizes.items():
    print(f"  {name} -> {size}B")

# set — like HashSet
tags = {"rag", "agent", "rag"}
print("set:", tags)
print("union/intersection:", tags | {"mcp"}, tags & {"rag", "mcp"})

# tuple — fixed, immutable; great for returning several values
point = (3, 4)
x, y = point
print("tuple:", point, x, y)

# Comprehensions — streams in one line
nums = list(range(10))
print("squares of evens:", [n * n for n in nums if n % 2 == 0])
print("word lengths:", {w: len(w) for w in models})
print("unique lower:", {t.lower() for t in ["RAG", "rag", "Mcp"]})

# Sorting with a key (like Comparator)
scores = {"doc1": 0.42, "doc2": 0.91, "doc3": 0.77}
ranked = sorted(scores, key=lambda k: scores[k], reverse=True)
print("ranked:", ranked)
print("top pair:", max(scores.items(), key=lambda kv: kv[1]))

# zip and enumerate
for i, (name, score) in enumerate(zip(["a", "b"], [0.1, 0.2]), start=1):
    print(f"  {i}. {name}={score}")

# Counter and defaultdict
words = "the cat and the hat and the bat".split()
print("counter:", Counter(words).most_common(2))
by_letter = defaultdict(list)
for w in words:
    by_letter[w[0]].append(w)
print("grouped:", dict(by_letter))

# any / all
print("any > 0.9:", any(s > 0.9 for s in scores.values()))
print("all > 0.4:", all(s > 0.4 for s in scores.values()))
