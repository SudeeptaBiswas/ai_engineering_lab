# Glossary: Python + pytest keywords

A–Z. One line each, with the Java twin. Topic = where it was taught.
Process + quiz: [REVIEW_01_python.md](REVIEW_01_python.md).

| Term | Plain meaning | Java twin / example | Topic |
|---|---|---|---|
| `__init__` | the constructor | `Point(...)` constructor | 1.4 |
| `__name__ == "__main__"` | true only when the file is run, not imported | `public static void main` | 1.1, 1.5 |
| `__repr__` / `__str__` | debug text / user text of an object | `toString()` | 1.4 |
| ABC + `@abstractmethod` | an explicit contract that fails early if a method is missing | `interface` | 1.4 |
| `approx` (pytest) | float compare with a tiny allowed error | `assertEquals(0.15, x, 1e-6)` | 1.9 |
| `assert` (pytest) | the check; on fail pytest prints both sides | `assertEquals` | 1.9 |
| `BaseModel` (pydantic) | a class whose type hints are checked at runtime | record + Jackson + Bean Validation | 1.6 |
| `capsys` | pytest fixture that captures `print()` output | a fake `System.out` | 2.6 |
| Comprehension | build a list/dict/set in one line | `stream().map().filter()` | 1.3 |
| `ConfigDict(extra="forbid")` | unknown keys are an error, not silently ignored | `@JsonIgnoreProperties(ignoreUnknown = false)` | 1.6 |
| `copy.deepcopy(x)` | a full copy, nested lists/dicts too; later changes to x don't show | deep `clone()` | 3.2 |
| `Counter` | counts items | `Map<K, Integer>` + loop | 1.3 |
| `@dataclass` | `__init__`, `__repr__`, `__eq__` written for you | `record` / Lombok `@Data` | 1.4 |
| `Decimal` | exact decimal number; `Decimal("8.00") == Decimal("8")`; bad text → `InvalidOperation` | `BigDecimal` (but `equals` checks scale) | 3.1 |
| `dict` | key → value, keeps insert order | `HashMap` | 1.3 |
| Duck typing | if it has `.run()`, you can call `.run()` | no `implements` needed | 1.4 |
| `encoding="utf-8"` | always set it on Windows | Windows default is not UTF-8 | 1.7 |
| Exception chain (`raise ... from`) | wrap an error, keep the cause in `__cause__` | `new X(msg, cause)` | 1.5 |
| `except` order | first match wins: child before parent | same as `catch` | 1.5 |
| f-string | `f"a{n}"` | `"a" + n` | 1.2 |
| Fake | stand-in for a real dependency in a test | Mockito `when(...).thenReturn` | 1.9 |
| `Field(...)` (pydantic) | rules on one field: `min_length=1`, `ge=1, le=5`, `strict=True` | `@NotBlank`, `@Min`, `@Max` | 1.6 |
| `field(default_factory=list)` | safe list default in a dataclass | `items: list = []` is an error | 1.4 |
| `@field_validator(..., mode="before")` | your code runs before the check, e.g. clean " Billing." → "billing" | a Jackson deserializer | 1.6 |
| Fixture | function pytest runs before a test; matched by parameter name | `@BeforeEach` | 1.9 |
| Floor division `//` | integer result | `7 // 2` = 3; `7 / 2` = 3.5 | 1.2 |
| `frozen=True` | immutable dataclass | immutable record | 1.4 |
| Generator (`yield`) | function that hands out values one at a time, pausing between | `Iterator` | 2.6 |
| `get_args(Label)` | the values inside a `Literal`, as a tuple | `Label.values()` | 1.6 |
| `httpx` | HTTP client | `HttpClient` | 1.7 |
| `is` vs `==` | same object vs same value | `==` vs `.equals()` | 1.2 |
| `json.loads` / `json.dumps` | text → dict / dict → text | Jackson `readValue` / `writeValueAsString` | 1.7 |
| Lax vs strict (pydantic) | lax converts when clear (`"3"` → 3, `true` → 1); strict refuses | Jackson coercion on / off | 1.6 |
| `Literal["a", "b"]` | only these exact values (case-sensitive) | `enum` | 1.6 |
| `localhost` vs `127.0.0.1` | localhost tries IPv6 first on Windows | 2.16 s vs 0.02 s per call | 1.7 |
| Marker (`@pytest.mark.x`) | a label; `-m "not x"` skips, `-m x` runs only those | `@Tag("x")` | 1.9 |
| `model_json_schema()` | a pydantic model's rules as a JSON Schema dict | Jackson `JsonSchemaGenerator` | 3.2 |
| `model_validate_json` | JSON text → checked object in one step; `model_dump()` back to dict | `mapper.readValue(json, X.class)` | 1.6 |
| Module | one .py file: many functions, constants, classes | (Java: one class per file) | 1.5 |
| `monkeypatch.setattr` | swap a function for one test, put back after | Mockito | 1.9 |
| Mutable default | `def f(x=[])` shares ONE list across calls | fix: `x=None` | 1.3 |
| Package | folder + `__init__.py` | Java package = folder | 1.5 |
| `parametrize` | one test, many rows, each its own result | `@ParameterizedTest` | 1.9 |
| `pathlib.Path` | file paths; `p / "a.txt"` | `java.nio.file.Path` | 1.7 |
| `@property` | a getter that reads like a field | getter | 1.4 |
| `pyproject.toml` | project + dependencies | `pom.xml` | 1.1 |
| `python -m package` | runs the package's `__main__.py` | `Main-Class` in a jar manifest | 2.6 |
| `raise_for_status()` | turn a 4xx/5xx into an exception (404 is not one by itself) | `if (code >= 400) throw` | 1.7 |
| `raises` (pytest) | test passes only if that error happens | `assertThrows` | 1.9 |
| `reversed()` | walk a list from the end | `Collections.reverse` / `descendingIterator` | 3.1 |
| `self` | the current object, written out | `this` | 1.4 |
| `set` | unique items, fast `in` | `HashSet` | 1.3 |
| Slicing | `nums[1:4]`, `[-2:]`, `[::2]` | `subList` (no full twin) | 1.3 |
| `split(":", 1)` | cut at the first `:` only (1 = max cuts) | `split(":", 2)` (2 = max parts) | 3.1 |
| `splitlines()` | text → list of lines, any line ending | `s.lines().toList()` | 3.1 |
| Spy | a fake that writes down what it received | Mockito `verify` / captor | 1.9 |
| `str.find` / `str.rfind` | index of the first / last match, -1 if none (no exception) | `indexOf` / `lastIndexOf` | 3.2 |
| `sys.path` | where imports are looked up: script folder, then .venv | classpath | 1.5 |
| Timeout | always give one on HTTP calls | 500-token answer took ~70 s | 1.7 |
| `TransportError` (httpx) | parent of ConnectError + ConnectTimeout | catch the parent for both | 1.5, 1.7 |
| Truthy / falsy | `0`, `""`, `[]`, `{}`, `None` are false | `if items:` = not empty | 1.2 |
| `try / except / else / finally` | `else` runs only if no error | try/catch/finally | 1.5 |
| `tuple` | fixed, immutable sequence; unpack with `a, b = t` | record / `List.of` | 1.2, 1.3 |
| `TypedDict` | a dict with known keys; checked by pyright, plain dict at runtime | a record, compile-time only | 2.6 |
| `uv` | installs Python + packages, runs files | Maven / Gradle | 1.1 |
| `uv.lock` | exact versions; commit it | Gradle lockfile | 1.1 |
| `ValidationError` (pydantic) | lists ALL problems: `loc`, `type`, `msg` each (not `ValueError`) | `ConstraintViolationException` | 1.6 |
| `.venv` | per-project packages, git-ignored | (no shared `~/.m2`) | 1.1 |
| `with` | closes the file/client for you, even on error | try-with-resources | 1.7 |
