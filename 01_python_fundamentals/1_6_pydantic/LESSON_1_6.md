# 1.6 Type hints + pydantic (~2 h)

Basic level. Comes after 3.1 (the order is in PLAN.md) because 3.2 needs it:
3.2 asks the model for JSON and checks it with pydantic. No Ollama today.

All numbers **measured on 10284Sudee**, pydantic 2.14.3, 2026-11-12.

## The question of this lesson
In 3.1 you checked one word by hand (`parse_label`). In 3.2 the model will
send a whole ticket as JSON: text, label, priority, tags. Checking every
field by hand gets long fast. Can the type hints do the checking?

They can't by themselves. **pydantic** can: it reads the same hints and
checks the data **when the code runs**.

## Java → Python map
| Java | Python |
|---|---|
| javac checks types | pyright checks hints (before run) |
| JVM checks casts at run time | nothing, unless you use pydantic |
| `enum Label { BILLING, ... }` | `Literal["billing", ...]` |
| `record Ticket(...)` + Jackson | `class Ticket(BaseModel)` |
| `@NotBlank`, `@Min(1)`, `@Max(5)` | `Field(min_length=1)`, `Field(ge=1, le=5)` |
| `mapper.readValue(json, Ticket.class)` | `Ticket.model_validate_json(json)` |
| `ConstraintViolationException` | `ValidationError` |
| `@JsonIgnoreProperties(ignoreUnknown = false)` | `ConfigDict(extra="forbid")` |

## 1. Type hints are notes, not checks
You have written hints since 1.4, and pyright (strict) checks them. That
works for **your** code. It does not work for data from outside:

- `TicketData(text=5, priority="high")` runs fine, though pyright flags
  it in the editor. A dataclass does not check types.
- `json.loads(...)` returns `Any`. Write `ticket: TicketDict = json.loads(...)`
  and pyright believes you. Measured: `"label": "refund"` got through
  with no error. `"priority": "high"` crashed later, inside `describe()`,
  with `'>=' not supported between instances of 'str' and 'int'`, far
  from where the bad data came in.
- Checking by hand works (`isinstance`, `in`), but it's one `if` per
  rule, and you write it again for every model.

Honest type for unchecked outside data: `object` or `dict[str, object]`,
never the type you hope for.

> ▶ **Now run part 1** (instant):
> `uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_1_hints.py`

## 2. pydantic: the hints become rules
```python
class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1)
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)
    tags: list[str] = []
```
- `Ticket.model_validate_json(text)` = parse + check in one step.
  `model_validate(a_dict)` for a dict. You get a real object back:
  `ticket.priority + 1` is maths, not text.
- Back out: `model_dump()` gives a dict, `model_dump_json()` gives text.
- Bad data raises `ValidationError` with **every** problem at once. For
  `{"text": "", "label": "refund", "priority": 9}` it gave 3 problems:
  `string_too_short`, `literal_error`, `less_than_equal`. Each problem
  is a dict: `loc` (where), `type` (a code), `msg` (for people).
- `loc` is a path: `("priority",)`, or `("tags", 1)` for the 2nd tag.
  An empty `()` means the whole input, e.g. `json_invalid` for text that
  isn't JSON.
- Unknown key `"team"`: ignored by default. With `extra="forbid"` it's an
  error (`extra_forbidden`). For model output, forbid: an extra key
  means the model didn't follow your format.
- `@field_validator("label", mode="before")` runs your code **before**
  the type check. It's used here to clean `" Billing."` to `billing`,
  the 3.1 cleaning moved into the model.

## 3. Lax vs strict
By default pydantic is **lax**: it converts when the meaning is clear.

| JSON `priority` | lax (default) | `Field(strict=True)` |
|---|---|---|
| `3` | 3 | 3 |
| `"3"` | 3 | error `int_type` |
| `true` | **1** | error `int_type` |
| `2.5` | error `int_from_float` | error |
| `"high"` | error `int_parsing` | error |

`true` → 1 surprises Java developers. Use strict when the source should
already send the right type. Lax is fine when the data comes from a form
or query string, where everything is text.

**Speed:** 10 000 validations took 0.045–0.089 s, which is 4.5–8.9 µs each
(3 runs). One Ollama call in 3.1 took ~0.7 s (5.9 s for 8, BISWAS). Checking costs nothing
next to the model.

> ▶ **Now run part 2** (instant):
> `uv run python 01_python_fundamentals/1_6_pydantic/examples_1_6_2_pydantic.py`

## 4. Things that bite
- **Literal is case-sensitive.** `"Billing"` fails, so clean it first
  (`mode="before"`).
- **`ValidationError` is from pydantic,** not Python's `ValueError`. Import it.
- **`= []` is safe in a model** (pydantic copies it), but still not in a
  `def` (1.3).
- **pydantic checks the shape, not the truth.** `"label": "bug"` for a
  billing ticket is valid. Measuring how often it's right is 3.1's
  `score`, and later evals (5.1).

## 5. Where it is used next
| Lesson | Uses |
|---|---|
| 3.2 Structured output | the model writes JSON; `Ticket.model_validate_json` checks it, and a retry on `ValidationError` |
| 3.3 Tool calling | tool arguments from the model, checked by a model class |
| 8.1 FastAPI | request and response bodies are pydantic models |

## Exercises: make the tests pass
You write the `Ticket` fields and 3 functions in
[models_1_6.py](models_1_6.py). The spec is
[exercises_1_6.py](exercises_1_6.py): 19 tests, no Ollama.

| What | Does | Tests |
|---|---|---|
| `Ticket` | fields, rules, clean label, forbid extra | 10 |
| `parse_ticket` | JSON → Ticket, or None | 3 |
| `error_fields` | each problem's `loc` as `"tags.1"`; `()` → `"(input)"` | 4 |
| `count_labels` | tickets per label, plus `"invalid"` | 2 |

```
uv run pytest 01_python_fundamentals/1_6_pydantic/exercises_1_6.py -v
```
Reference solution, measured: **19 passed in 0.17–0.19 s** (3 runs),
pyright 0.
