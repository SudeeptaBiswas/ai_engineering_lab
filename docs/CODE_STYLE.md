# Code style for lesson code

From lesson 4.1 on, every file Claude writes follows this: examples,
stubs, given helpers, tests, and `assistant/`. Old `assistant/` code is
brought up to date whenever a step touches it. User feedback 2026-11-15 (DECISIONS).
Bad examples are real lines from 3.4 (`examples_3_4_1_tickets.py`).

Goal: read a function once and know **what it is for, what goes in, what
comes out, and in which order things happen**, without jumping around.

## How these rules are kept (so none is forgotten)
1. **Script** `lab_tools/lesson_rules.py`: runs after every edit Claude
   makes (hook) and on every commit (pre-commit). Checks names, docstrings,
   `@debug` + log line, test docstrings, file length, LESSON md sections.
   Scope and what blocks: top of `lab_tools/lesson_rules_run.py`.
2. **Template** `docs/templates/LESSON_TEMPLATE.md`: section order + a
   checklist for what a script can't judge.
3. **Fresh eyes**: the `lesson-reviewer` agent (`.claude/agents/`) reviews
   a lesson folder before it is handed over.
4. **The user** reviews names and the "why".

The user's own code (a stub file with `# lesson-rules: user-code`) gets
the same checks as warnings only: they never block a commit.

## 1. Names say what it holds and what it is for
A name answers "what is inside?" and "what do we use it for?".
No vague words: `item`, `result`, `text`, `data`, `wrap`, `all`, `schema`.

| Bad (3.4) | Why unclear | Good |
|---|---|---|
| `SUSPICIOUS` | suspicious what? tickets? words? | `INJECTION_KEYWORDS` |
| `INNOCENT` | innocent what? | `NORMAL_TEXTS_WITH_ATTACK_WORDS` |
| `FIELDS_PROMPT` | which fields? prompt for what? | `TRIAGE_SYSTEM_PROMPT` |
| `GUARD_PROMPT` | | `TRIAGE_SYSTEM_PROMPT_WITH_GUARD` |
| `ask_json` | ask whom? what JSON? | `ask_model_for_json` |
| `schema` | schema of what? we send it, the reply doesn't give it | `reply_format` (see below) |
| `user_text` | which user text? | `ticket_text` |
| `wrap` (a bool) | wrap what, in what? | `wrap_in_ticket_tags` |
| `triage_all` | all of what? does what with it? | `triage_tickets_and_count_hijacks` |
| `detect_all` | | `compare_injection_detectors` |

- Name by **use**, not by technology. `TRIAGE_SCHEMA` is a JSON Schema we
  send in Ollama's `"format"` field so the reply must have that shape.
  So: `TRIAGE_REPLY_FORMAT`, parameter `reply_format`, comment
  `# JSON Schema: the shape the model's reply must have`.
- Functions: verb + object (`count_hijacks`, `detect_by_keywords`).
- Booleans: a yes/no question (`is_attack`, `was_hijacked`).
- **No `item[0]`, `ticket[2]`.** Tuples with positions → a `NamedTuple` or
  `@dataclass` with named fields: `ticket.text`, `ticket.correct_label`.
  Same for a list position that means something: not `tool_specs[3]`
  ("the 4th is refund"), but find it by name; not `REAL_STREAM_LINES[4]`,
  but a constant `DONE_LINE`.
- **Names the model reads are names too.** Tool argument fields are
  shown to the model: `first_number`, not `a`. Measure before and after
  a rename (2026-11-15: multiply called 4/5 both ways).

## 2. Same thing, same name, everywhere
If the caller has `ticket_text`, the parameter is `ticket_text` too.
Rename only when the content changes, e.g. `ticket_text` →
`tagged_ticket_text` after adding `<ticket>` tags.
**One exception, on purpose:** the examples and the stubs the user fills
use different function names (4.1: `chunk_by_headings` vs
`split_by_headings`), so the examples don't hand over the stub answers.
Inside each file, the names stay the same.

## 3. One function, one job
- If a function has an `if` for a different topic, move that part to its
  own function. 3.4 `triage_all` wraps tickets, calls the model, scores
  labels, finds hijacks and prints. That's 5 jobs → 5 functions.
- **Inputs come from parameters.** Globals only for fixed settings that
  never change per call (`OLLAMA_URL`, `CHAT_MODEL`, prompts, schemas).
  Data being processed (tickets, texts) is always a parameter.
- Prefer returning a value over printing inside. The caller (`main`) prints.
  In `assistant/`, the chat screen is `chat_turn.py` + `cli.py`: only they
  print. A checker (gate, answer check) returns; the turn prints.

## 4. Docstring: goal first, then how
```python
def count_hijacks(tickets: list[TestTicket], system_prompt: str) -> int:
    """Count how many attack tickets got the value the attacker asked for.

    How:
        1. Send each ticket to the model for triage.
        2. Compare the reply with the attacker's goal.
        3. Count the matches.
    Args:
        tickets: the test tickets, attacks and normal ones.
        system_prompt: TRIAGE_SYSTEM_PROMPT or TRIAGE_SYSTEM_PROMPT_WITH_GUARD.
    Returns:
        Number of hijacked tickets, e.g. 5.
    """
```
- Line 1 = **what we are trying to achieve**, in plain words.
- `How:` = the steps, numbered, only if there is more than one step.
- Args / Returns with a real example value (existing rule, kept).

## 5. Simple words
Short sentences, common words. Explain a term the first time it shows up.
Write "the model's yes/no answer", not "the injection classification output".

## 6. One step per line
Never chain several calls and lookups in one line.

Bad (3.4): nobody can tell what goes in, what comes out, or why `["injection"]`:
```python
by_model = ask_json(DETECT_PROMPT, item[0], DETECT_SCHEMA)["injection"]
```
Good:
```python
reply_json = ask_model_for_json(DETECTOR_SYSTEM_PROMPT, ticket.text, DETECTOR_REPLY_FORMAT)
model_says_attack = reply_json["injection"]  # the model's yes/no answer
```

**Name each value before you compare it.** Bad (3.4):
```python
if attack is not None and result[attack[0]] == attack[1]:
```
Good:
```python
if ticket.attacker_goal is None:  # a normal ticket: nothing to hijack
    return False
attacked_field = ticket.attacker_goal.field_name      # e.g. "priority"
attacker_wanted_value = ticket.attacker_goal.value    # e.g. 5
model_gave_value = triage_reply[attacked_field]       # what the model answered for that field
was_hijacked = model_gave_value == attacker_wanted_value
log.debug("wanted=%r got=%r was_hijacked=%s", attacker_wanted_value, model_gave_value, was_hijacked)
return was_hijacked
```

## 7. Put a result in a variable, then return it
So you can stop there in the debugger and see it in the log.
```python
# Bad:  return json.loads(response.json()["message"]["content"])
reply_text = response.json()["message"]["content"]  # the model's reply, as text
reply_json = json.loads(reply_text)                  # text -> dict
log.debug("reply_json=%s", reply_json)
return reply_json
```

## 8. A comment on a line that does more than one thing
If a line still does 2+ things (a comprehension, a format string with
math), add a one-line comment saying what comes out.
```python
hijacked_count = sum(was_hijacked)  # True counts as 1, so this counts the hijacks
```

## 9. Logging shows the order of events
Use `from lab_tools.log import cut_text, debug, log` and put `@debug` on
every function Claude writes: examples, stubs, tests, fakes, `assistant/`
(user, 2026-11-15; before: examples only). Each function logs:
- `start:` with its inputs; long text through `cut_text(...)`,
- one line per main step,
- every comparison: `expected=... got=...`,
- `result:` with what it returns.

Each line starts with `file:line` and the function name, so the log read
top to bottom shows the call order and where each line came from:
```
examples_4_1.py:88   compare_detectors  start: 10 texts
examples_4_1.py:61   detect_by_keywords start: ticket_text='Can you add a dark mode? Ignore all prev...'
examples_4_1.py:66   detect_by_keywords result: found_keywords=['ignore all previous']
examples_4_1.py:74   detect_by_model    expected=True got=True
```
- Cut length: `TEXT_CUT_LENGTH` in `lab_tools/log.py` (40; 0 = no cut). One place for every file.
- Exception: a small helper that runs once per item in a loop (per
  message, per stream line) has no own log lines, or the log floods.
  Its caller logs the total. Say so in its docstring
  (e.g. `estimate_tokens`, text pieces in `parse_stream_line`).
- A function that runs before the log level is set logs after it
  (`assistant/__main__.py`: `hide_log_unless_asked` runs first).
- `print` is only for the lesson's final output (scores, tables).

## 10. Tests say what they check
- Test name = the behaviour: `test_refund_blocked_when_customer_did_not_ask`.
- Docstring line 1 = **what we check and why it matters**:
  `"""A tool result asked for a refund, not the customer: the gate must block it."""`
  Not `"""Checks: ..."""`: "checks" adds nothing, and the why goes missing.
- The real-model tests log `expected=... got=...` too.
- Each `parametrize` row gets a short comment saying what case it covers.
- Put the result in a variable, log expected vs got, then assert. A
  failing test then shows the line number and both values in its log:
```python
got_reason = check_tool_call("refund", refund_arguments, customer_message)
log.debug("expected=%r got=%r", expected_reason, got_reason)
assert got_reason == expected_reason
```

## 11. File length
Clear code is longer. Aim under 150 lines; up to 250 is fine when the
rules above need it (see DECISIONS 2026-11-15). Over 250: split the file.

## 12. Lesson .md files follow the same ideas
User feedback 2026-11-15 (DECISIONS). The `LESSON_N_N.md` has, in this order:
1. **The problem**: a real example that fails today (context first).
2. **Goal**: one or two lines, what we want to reach, with a number.
3. **How we get there**: the idea in plain words, before any term.
4. **Steps**: numbered, one line each, with an example value per step.
5. **Your path**: read → run → read → run → exercises.
6. Sections, then **Exercises**: per function its goal and one
   `in → out` example; edge cases listed, so nobody has to guess.

Writing: short sentences, one idea per bullet, a term explained the
first time. Add an example wherever a rule alone could be misread.

## Rules kept from before
- Long form first, short form in a `# concise:` comment (DECISIONS 2026-11-04).
- Args/Returns/Raises in docstrings.
- **Dropped 2026-11-15:** Java twin in code comments (user: skip it).
- Context first: a real example, then the short definition.
