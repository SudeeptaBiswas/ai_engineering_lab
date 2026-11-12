# 3.3 Raw tool calling over HTTP (~2.5 h)

Basic level. Uses 3.2 (JSON Schema + pydantic checks) and 2.3 (chat API).
Next: 3.4 prompt injection, then assistant v2 gets these tools.

All numbers **measured on BISWAS** (CPU only), Ollama 0.40.16,
qwen3:1.7b, temperature 0, seed 42, 2026-11-13. Part 2 scores were the
same in 2 runs; times vary by a few seconds.

## The question of this lesson
Ask the model "What is 4821 * 3967?" with no tools. It writes out a long
multiplication, step by step. 3 runs gave 3 different answers:
19124907 (right), 18125007, 120625. Ask "Where is my order A-1001?" and
it can't know: your order data isn't in its training. It can't know
today's date either (2.1).

The fix: let **your code** do the work. You tell the model which functions
exist. It replies "please call `multiply(a=4821, b=3967)`". You run it, send
back the result, and the model writes the answer.

**Tool calling** = the model asks your code to run a named function with
JSON arguments, and then uses the result. The model never runs anything.

## Java → Python map
| Java | Python |
|---|---|
| Spring AI / LangChain4j `@Tool` method | a function + a pydantic args model + a description |
| LangChain4j `ToolSpecification` | `tool_spec()`: name, description, JSON Schema |
| `Map<String, Tool>` + lookup | `TOOLS[name]` (a dict) |
| `Function<Args, String>` | `Callable[[Any], str]` |
| `try { ... } catch (ConstraintViolationException e)` | `try: model_validate(...) except ValidationError` |

## 1. One call by hand
Add a `"tools"` list to the 2.3 body. Each tool = name + description +
a JSON Schema for its arguments (3.2). When a tool fits, the reply has
empty `content` and a `tool_calls` list:

```json
{"id": "call_meu46p5w",
 "function": {"index": 0, "name": "multiply", "arguments": {"a": 4821, "b": 3967}}}
```

`arguments` is already a dict, not JSON text. Then:

```
[user]                                  → reply: tool_calls = multiply(4821, 3967)
[user, reply, tool("19124907")]         → reply: "The result ... is 19124907."
```

Send back the model's **own reply** (it must see what it asked), then one
`{"role": "tool", "tool_name": "multiply", "content": "19124907"}` per call.

- **Two questions, two calls** in one reply: `multiply(12.5, 8)` and
  `multiply(7, 6)`. Run both, send both results.
- **No tool fits** ("capital of France?"): a plain answer, no call.

| 5 products | Right | Time |
|---|---|---|
| model alone | 2/5 | 107.0 s (122.9 s in a 2nd run) |
| with the tool | **5/5** | 24.3 s (37.6 s) |

Faster too: one short call instead of a long worked answer.

> ▶ **Now run part 1** (needs Ollama, ~3 min).
> `uv run python 03_prompting_tools/3_3_tool_calling/examples_3_3_1_calls.py`

## 2. The loop, and what the description does
One call is not enough in general: after a result the model may ask for
another. So loop: POST → tool calls? run them, POST again → no calls?
that text is the answer. Stop after N rounds (it may never stop).

3 tools (`multiply`, `order_status`, `today`), 8 questions: **7/8 right**,
30.1–34.8 s. The miss: "Where is my order 1002?" (no `A-`). The model
replied "cannot be determined without accessing the order database" and
**never called the tool**. It had the tool and still said it couldn't.

The model only reads the **description + schema**. Same order tool, 3 ways:

| Description | "order A-1001?" | "order number 1001" | "order 1002?" |
|---|---|---|---|
| "Look up an order by its id, e.g. A-1001." | called, right | called with `"1001"` → error | no call |
| "Look up the status of an order." (no example) | **no call** | called with `"1001"` → error | no call |
| no example, but the field described | called, right | called with `"1001"` → error | no call |

- **An example in the description helps here.** In 3.2 an example in the
  prompt got *copied*. Here it shows what an id looks like. Without one,
  the model didn't call the tool even for "A-1001".
- **An error result is not a retry.** With `"1001"` the tool said "must look
  like A-1001". The model passed that on to the user ("not in the format
  required") and never tried `"A-1001"` itself.
- **Make the tool forgiving.** Accept `"1001"` as `"A-1001"` in code: then
  "order number 1001" was answered right. Fix in code what code can fix.
  Our `OrderArgs` does it in a `field_validator` (1.6).

> ▶ **Now run part 2** (needs Ollama, ~1.5 min).
> `uv run python 03_prompting_tools/3_3_tool_calling/examples_3_3_2_loop.py`

## 3. Things that bite
- **Says it will, doesn't.** No `tool_calls` = the loop ends, even if the
  text says "Let me check that for you." Seen while preparing this lesson.
- **A call written as text.** Once, with a different prompt, the reply was
  `'{"name": "order_status", "arguments": {...}}'` in `content`, with no
  `tool_calls`. Code treated it as the answer.
- **Bad arguments must not crash the loop.** Validate with pydantic; send
  the errors back as the tool's result (`"error: b: Field required"`). Same
  idea as the 3.2 retry, but the model decides what to do next.
- **Never trust the arguments.** The model picks them. A `delete_order`
  tool would delete whatever id it writes (3.4).
- **qwen3:4b** (one try while preparing): thinking leaked into `content`,
  43–80 s per question, 1 of 3 order questions called. Stay on 1.7b.

## 4. Where it is used next
| Lesson | Uses |
|---|---|
| assistant v2 | the same 3 tools in the real chat app |
| 3.4 Prompt injection | text in a ticket or tool result that asks the model to call a tool |
| 6.1 Agent loop | this loop, plus planning between calls |
| 6.2 Tool design | descriptions, forgiving arguments, error texts |
| 7.3 MCP server | the same name + description + input schema, served to any AI client |

## Exercises: make the tests pass
The tools are given in [toolbox_3_3.py](toolbox_3_3.py): 3 args models,
3 functions, the `TOOLS` dict. Read it first. You write the 4
`raise NotImplementedError` functions in [tool_calls_3_3.py](tool_calls_3_3.py).
The spec is 2 test files: [exercises_3_3_1_tools.py](exercises_3_3_1_tools.py)
(first 3 functions) and [exercises_3_3_2_loop.py](exercises_3_3_2_loop.py)
(`ask`). 22 tests without Ollama + 2 real.

| Function | Does | Tests |
|---|---|---|
| `tool_spec` | one `"tools"` entry; parameters = the args model's schema | 3 |
| `chat_body` | the POST body with every tool | 2 |
| `run_tool` | look up, validate, run; problems as `"error: ..."` text, never raise | 12 |
| `ask` | the loop: tool calls → results → POST again; None after max rounds | 5 fake + 2 real |

```
uv run pytest 03_prompting_tools/3_3_tool_calling -v
```
Ollama off? Add `-m "not ollama"`. Reference solution, measured:
**24 passed in 10.86–12.06 s** (3 runs), 22 + 2 deselected in 0.26 s,
pyright 0. The stubs: 24 failed.
