"""Replace each `...` with code. Run until every line says PASS."""


def fizzbuzz(n: int) -> str:
    """'Fizz' if n divisible by 3, 'Buzz' by 5, 'FizzBuzz' by both, else str(n)."""
    if n % 5 == 0 and n % 3 == 0:
        return "FizzBuzz"
    elif n % 5 == 0:
        return "Buzz"
    elif n % 3 == 0:
        return "Fizz"
    else :
        return str(n)

def average(nums: list[float]) -> float:
    """Average of nums. Return 0.0 for an empty list (hint: truthy check)."""

    return 0.0 if len(nums) == 0 else (sum(nums) / len(nums))


def count_vowels(text: str) -> int:
    """Count a, e, i, o, u (any case). Hint: `for ch in text.lower():`"""
    vowels =  "aeiou"
    count = 0
    for s in text.lower():
        if s in vowels:
            count += 1
    return count


def token_cost(tokens: int, price_per_1k: float = 0.002) -> float:
    """Cost of `tokens` at `price_per_1k` per 1000 tokens, rounded to 4 places."""
    return round((tokens/1000) * price_per_1k , 4)




def split_even_odd(nums: list[int]) -> tuple[list[int], list[int]]:
    """Return (evens, odds), keeping the original order."""
    evens: list[int] = []
    odds: list[int] = []
    for i in nums:
        if i % 2 == 0:
            evens.append(i)
        else:
            odds.append(i)

    return evens, odds

def check(label: str, got: object, expected: object) -> None:
    status = "PASS" if got == expected else f"FAIL (got {got!r}, expected {expected!r})"
    print(f"{label:<16} {status}")


if __name__ == "__main__":
    check("fizzbuzz 15", fizzbuzz(15), "FizzBuzz")
    check("fizzbuzz 9", fizzbuzz(9), "Fizz")
    check("fizzbuzz 10", fizzbuzz(10), "Buzz")
    check("fizzbuzz 7", fizzbuzz(7), "7")
    check("average", average([1, 2, 3, 4]), 2.5)
    check("average empty", average([]), 0.0)
    check("count_vowels", count_vowels("Retrieval AUGMENTED"), 8)
    check("token_cost", token_cost(1500), 0.003)
    check("token_cost named", token_cost(2000, price_per_1k=0.01), 0.02)
    check("split_even_odd", split_even_odd([1, 2, 3, 4, 5]), ([2, 4], [1, 3, 5]))
