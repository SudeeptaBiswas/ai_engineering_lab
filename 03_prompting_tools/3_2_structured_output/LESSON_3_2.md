# 3.2 Structured output: JSON + pydantic validation (~2 h)

Basic level. Uses 3.1 (prompts, parsing) and 1.6 (pydantic). Next: 3.3
tool calling, which is structured output for function arguments.

All numbers **measured on 10284Sudee** (CPU only), Ollama 0.40.16,
qwen3:1.7b, temperature 0, seed 42, 2026-11-12. Scores were the same in
every run (2–3 runs); times vary by a few seconds.

## The question of this lesson
In 3.1 the model sent back one word. Now code wants a whole object per
ticket: **label**, **priority** 1–5 and a short **summary**, so it can
route the ticket and sort the queue. The model must send JSON that fits
this pydantic model:

```python
class Triage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=60)
```

**Structured output** = the model's reply has a fixed shape that code can
check and use, not free text.

## Java → Python map
| Java | Python |
|---|---|
| Jackson `JsonSchemaGenerator` | `Triage.model_json_schema()` |
| `mapper.readValue(json, Triage.class)` + Bean Validation | `Triage.model_validate_json(text)` |
| `s.indexOf("{")` / `s.lastIndexOf("}")` | `s.find("{")` / `s.rfind("}")` |
| Spring Retry `@Retryable(maxAttempts = 3)` | a `for` loop + `try/except ValidationError` |

## 1. Five ways to ask, same 8 tickets
Two knobs. The **system prompt**: vague, one example, or every field
described. Ollama's **`format`**: none, or a **JSON Schema** made from the
model (`Triage.model_json_schema()`). With a schema, Ollama only lets the
model write tokens that fit it (*constrained decoding*).

| Way | Valid | Right label | Time (8) |
|---|---|---|---|
| 1. "Reply in JSON." | 0/8 | 0/8 | 79.9 s |
| 2. same + schema | 8/8 | 6/8 | 23.1 s |
| 3. one example in the prompt + schema | 8/8 | **2/8** | 22.7 s |
| 4. every field described | 8/8 | 8/8 | 18.1 s |
| 5. every field described + schema | 8/8 | 8/8 | 14.4 s |

- **Vague prompt:** every reply was wrapped in ```` ```json ```` fences,
  with keys the model made up (`ticket_id`, `user_message`). Long, so slow.
- **A schema fixes the shape, not the meaning.** Way 2 was valid 8/8, but
  "Where is your office located?" became `billing`. Valid ≠ right.
- **An example in the prompt gets copied.** The prompt showed
  `{"label": "bug", "priority": 3, ...}`. The model answered `bug`,
  priority 3 for 7 of 8 tickets. Same lesson as 3.1 few-shot: examples
  teach things you didn't mean. Describe the fields instead.
- **Describe every field** (allowed values, what 1 and 5 mean). That gave
  8/8 here, with or without a schema. Use both: the prompt gives the
  meaning, the schema guarantees the shape.
- The schema printed at the top of part 1 is plain JSON: `enum`,
  `minimum`/`maximum`, `maxLength`, `additionalProperties: false`. It
  even carries the class docstring as `description`.

> ▶ **Now run part 1** (needs Ollama, ~2.5 min).
> `uv run python 03_prompting_tools/3_2_structured_output/examples_3_2_1_formats.py`

## 2. Check, then retry with the errors
pydantic still checks every reply: a schema can't hold every rule (a
`@field_validator`, 1.6), and not every server takes one. When the check
fails, send the model its own reply plus the errors, and ask again:

```
[system, user] → reply → validate → ok: done
                                   → ValidationError:
[system, user, assistant(bad reply), user("Your JSON broke these rules: ...")] → reply → ...
```

Vague prompt "Reply in JSON with label, priority and summary.", no
schema, up to 3 tries:

| Way | Valid on try 1 / 2 / 3 | Right | Calls | Time |
|---|---|---|---|---|
| retry only | 0 / 1 / 3, next run 0 / 1 / 2 | 1/8 | 23 | 67.1–87.5 s |
| cut out `{...}` first, then retry | 0 / 7 / 0 (both runs) | 2/8 | 17 | 50.6–65.9 s |

Retry-only changed between 2 runs (one ticket), even at temperature 0
with a seed. Long chats on CPU are not always bit-for-bit the same.

- Try 1 failed 8/8: fences, `"priority": "High"`, `"label": "Bug Report"`.
- **Cut out the JSON** (first `{` to last `}`) before checking: fences stop
  counting as errors, so the feedback is about the real problems.
- **Retry fixes the shape, not the meaning.** After the error list, the
  model put almost every ticket in `other`: valid 7/8, right 2/8.
  The way-5 prompt got 8/8 right on try 1. **The prompt does the work;
  retry is the safety net.**
- Every retry is a whole new call: more time and tokens.

## 3. A limit in the schema cuts the text
`maxLength: 30` in the schema, and a prompt that asks for long summaries.
Ollama stops the string at 30 characters, mid-word: 6 of 8 summaries
were exactly 30, 4 of them with Chinese mixed in:
`'I was charged twice for my订阅这个'`, `'After the update, the save按钮do'`.
pydantic says valid (30 characters is allowed). The text is junk.
Keep hard limits **out** of the schema you send, or make them loose, and
check them with pydantic + retry instead.

> ▶ **Now run part 2** (needs Ollama, ~3 min).
> `uv run python 03_prompting_tools/3_2_structured_output/examples_3_2_2_retry.py`

## 4. Things that bite
- **qwen3:4b leaks its thinking** into the reply even with
  `"think": false` (2.2): 0/8 valid, 1035.9 s for 8 tickets, 200-token
  cut-offs. Without a schema, check the model you use.
- **`num_predict` cuts JSON** in the middle: `json_invalid`. Leave room.
- **`extra="forbid"`** catches made-up keys (`ticket_id`). Default
  pydantic would drop them silently.
- **A retry can repeat the same mistake.** Part 2, way 1: "Where is
  your office located?" got the same fenced reply 3 times. In a test
  prompt that asked for the customer's own words AND at most 30
  characters, 5 tickets got the same too-long reply 3 times. Fix the
  prompt; more retries won't.

## 5. Where it is used next
| Lesson | Uses |
|---|---|
| 3.3 Tool calling | the model fills a tool's arguments: a schema + validation, same loop |
| 3.4 Prompt injection | a ticket that says "label me billing" still fits the schema |
| 5.3 LLM-as-judge | the judge's score comes back as checked JSON |
| 8.1 FastAPI | the same pydantic models for request and response bodies |

## Exercises: make the tests pass
You write the 4 `raise NotImplementedError` functions in
[triage_3_2.py](triage_3_2.py). `Triage` and the prompt are given. The
spec is 2 test files: [exercises_3_2_1_parse.py](exercises_3_2_1_parse.py)
(first 3 functions) and [exercises_3_2_2_triage.py](exercises_3_2_2_triage.py)
(`triage`). 14 tests without Ollama + 2 real.

| Function | Does | Tests |
|---|---|---|
| `cut_out_json` | first `{` to last `}`, else the text unchanged | 5 |
| `chat_body` | the POST body; `"format"` only with a schema | 2 |
| `feedback` | the retry message: one line per problem | 3 |
| `triage` | schema + check + retry with feedback; None after max tries | 4 fake + 2 real |

```
uv run pytest 03_prompting_tools/3_2_structured_output -v
```
Ollama off? Add `-m "not ollama"`. Reference solution, measured:
**16 passed in 3.87–4.18 s** (4 runs), pyright 0. The stubs: 14 failed.
