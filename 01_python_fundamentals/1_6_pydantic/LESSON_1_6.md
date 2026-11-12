# 1.6 Type hints + pydantic (~2 h)

Basic level. It comes after 3.1 because 3.2 needs it. No Ollama today.

All numbers were **measured on 10284Sudee**, with pydantic 2.14.3, on 2026-11-12.

## The problem
In 3.1 you checked one word by hand (`parse_label`). In 3.2 the model
sends a whole ticket as JSON: text, label, priority and tags.
Checking every field by hand is a lot of code.

Type hints can't check it: Python ignores them when the code runs.
**pydantic** can: it reads your hints and checks the data **when the code runs**.

## Java → Python map
| Java | Python |
|---|---|
| javac checks types | pyright checks hints (before you run) |
| the JVM checks casts while running | nothing checks, unless you use pydantic |
| `enum Label { BILLING, ... }` | `Literal["billing", ...]` |
| `record Ticket(...)` + Jackson | `class Ticket(BaseModel)` |
| `@NotBlank`, `@Min(1)`, `@Max(5)` | `Field(min_length=1)`, `Field(ge=1, le=5)` |
| `mapper.readValue(json, Ticket.class)` | `Ticket.model_validate_json(json)` |
| `ConstraintViolationException` | `ValidationError` |
| `@JsonIgnoreProperties(ignoreUnknown = false)` | `ConfigDict(extra="forbid")` |

## 1. Hints are notes, not checks
pyright checks the hints in **your** code. It can't check data that
comes from outside, like JSON:

- A dataclass doesn't check types. `TicketData(text=5, priority="high")`
  runs without an error.
- `json.loads(...)` returns `Any`. If you write
  `ticket: TicketDict = json.loads(...)`, pyright just believes you.
- Measured: `"label": "refund"` got through with no error.
  `"priority": "high"` crashed later, inside another function:
  `'>=' not supported between instances of 'str' and 'int'`.
  The crash happened far from where the bad data came in.
- You can check by hand with `isinstance` and `in`, but you need one
  `if` per rule, for every model.

Tip: give outside data the type `object` or `dict[str, object]` until
it has been checked. Don't give it the type you hope for.

> ▶ **Now run part 1** (instant):
> `uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_1_hints.py`

## 2. pydantic: hints become rules
```python
class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1)
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []
```
- **In:** `Ticket.model_validate_json(text)` reads JSON text and checks
  it in one step. Use `model_validate(a_dict)` for a dict.
- You get a real object back: `ticket.priority + 1` adds numbers, not text.
- **Out:** `model_dump()` gives a dict, `model_dump_json()` gives JSON text.
- **Bad data** raises a `ValidationError` that lists **all** problems
  at once. Example: `{"text": "", "label": "refund", "priority": 9}`
  gave 3 problems: `string_too_short`, `literal_error`, `less_than_equal`.
- Each problem is a dict:
  - `loc` says where. It's a path: `("priority",)`, or `("tags", 1)` for
    the 2nd tag. `()` means the whole input, e.g. `json_invalid` when the
    text isn't JSON.
  - `type` is a short code; `msg` is text for people.
- **Unknown keys** like `"team"` are ignored by default.
  `extra="forbid"` makes them an error (`extra_forbidden`). Use it for
  model output: an extra key means the model broke your format.
- **Your own fix-up step:** `@field_validator("label", mode="before")`
  runs your code **before** the check. Here it turns `" Billing."` into
  `billing`, the same cleaning as 3.1.

## 3. Lax vs strict
By default pydantic is **lax**: it converts a value when the meaning is clear.

| JSON `priority` | lax (default) | `Field(strict=True)` |
|---|---|---|
| `3` | 3 | 3 |
| `"3"` | 3 | error `int_type` |
| `true` | **1** | error `int_type` |
| `2.5` | error `int_from_float` | error |
| `"high"` | error `int_parsing` | error |

- `true` → 1 surprises Java developers.
- Use **strict** when the sender should already send the right type.
- Use **lax** for forms and query strings, where everything arrives as text.

**Speed:** 10 000 checks took 0.045–0.089 s, so 4.5–8.9 µs each (3 runs).
One Ollama call in 3.1 took ~0.7 s (5.9 s for 8, BISWAS). Checking is
almost free next to the model.

> ▶ **Now run part 2** (instant):
> `uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_2_pydantic.py`

## 4. Watch out
- **Literal is case-sensitive.** `"Billing"` fails, so clean it first
  (`mode="before"`).
- **Import `ValidationError` from pydantic.** It's not Python's `ValueError`.
- **`= []` is safe in a model**, because pydantic copies it. It's still
  not safe in a `def` (1.3).
- **pydantic checks the shape, not the truth.** `"label": "bug"` on a
  billing ticket passes. To know how often the model is right, measure it
  (3.1 `score`, later 5.1 evals).

## 5. Used next in
| Lesson | How |
|---|---|
| 3.2 Structured output | the model writes JSON; `Ticket.model_validate_json` checks it; retry on `ValidationError` |
| 3.3 Tool calling | a model class checks the tool arguments the model sends |
| 8.1 FastAPI | request and response bodies are pydantic models |

## Exercises: make the tests pass
Write the `Ticket` fields and 3 functions in
[models_1_6.py](models_1_6.py). The tests in
[exercises_1_6.py](exercises_1_6.py) are the spec: 19 tests, no Ollama.

| What | Does | Tests |
|---|---|---|
| `Ticket` | fields, rules, clean label, no extra keys | 10 |
| `parse_ticket` | JSON → Ticket, or None | 3 |
| `error_fields` | each problem's `loc` as text, e.g. `"tags.1"`; `()` → `"(input)"` | 4 |
| `count_labels` | count tickets per label, plus `"invalid"` | 2 |

```
uv run pytest 01_python_fundamentals/1_6_pydantic/exercises_1_6.py -v
```
Reference solution, measured: **19 passed in 0.17–0.19 s** (3 runs), pyright 0.
