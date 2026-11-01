"""Python syntax next to Java. Run it, then read each block."""

# Variables: no type keyword. Type belongs to the value.
count = 3
price = 9.5
name = "Ollama"
active = True
nothing = None
print(type(count), type(price), type(name), type(active), type(nothing))

# f-strings replace String.format / concatenation
print(f"{name} costs {price:.2f}, count={count}")

# Division
print(7 / 2, 7 // 2, 7 % 2, 2**10)  # 3.5 3 1 1024

# if / elif / else — no parentheses needed
score = 72
if score >= 80:
    grade = "A"
elif score >= 60:
    grade = "B"
else:
    grade = "C"
print("grade:", grade)

# Ternary
label = "pass" if score >= 60 else "fail"
print("label:", label)

# Loops
for i in range(3):  # 0, 1, 2
    print("i =", i)

for idx, word in enumerate(["rag", "agent", "mcp"]):  # index + value
    print(idx, word)

n = 3
while n > 0:
    n -= 1  # no n--

# match (like switch, but more powerful)
command = "stop"
match command:
    case "start":
        print("starting")
    case "stop" | "halt":
        print("stopping")
    case _:
        print("unknown")


# Functions: defaults, keyword args, multiple returns
def describe(model: str, size_b: float = 4.0, *, local: bool = True) -> str:
    where = "local" if local else "cloud"
    return f"{model} ({size_b}B, {where})"


print(describe("qwen3"))
print(describe("llama3.2", 3, local=False))  # args after * must be named


def min_max(nums: list[int]) -> tuple[int, int]:
    return min(nums), max(nums)


lo, hi = min_max([3, 1, 4, 1, 5])
print("min/max:", lo, hi)

# Truthy / falsy
for value in [0, "", [], None, 1, "x", [0]]:
    print(repr(value), "->", bool(value))

# == compares value, `is` compares identity
a = [1, 2]
b = [1, 2]
print(a == b, a is b)  # True False
