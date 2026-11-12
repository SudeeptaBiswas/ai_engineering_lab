# Review: phase 03, Prompting + tool calling

Per topic: the **flow** (how the process runs), the **must-remember** points,
then a **quiz**. Click a question to see the answer. Say your answer first.
Keywords: [GLOSSARY_AI.md](GLOSSARY_AI.md).

## 3.1 Prompt patterns: system, few-shot, step-by-step
```
system (rules) + examples as past turns (few-shot) + question
  → model (temp 0, seed 42) → raw text
  → parse: clean, accept only an exact label / last "Answer:" line
  → score against expected answers → keep the pattern that wins
```
- **System = the rules.** One-word format: 0/8 → 8/8, and 5x faster (one word to write).
- **Few-shot = show, don't tell.** Examples go in as user/assistant turns. 6/8 → 7/8, but broke 1.
- **Step-by-step** gives the model scratch paper: maths 5/6 → 6/6. `think=True` same score, 4x slower.
- **Never trust the shape.** Parse and check: a sentence is not a label; compare numbers as numbers.
- **Measure, don't assume.** 8 tickets is too few to trust (5.1: 50+).

<details><summary>Q1. Zero-shot gave 0/8 usable labels. What fixed the format?</summary>A system message: "Reply with exactly one word: billing, login, bug, or other." 0/8 → 8/8.</details>
<details><summary>Q2. How do few-shot examples reach the model?</summary>As fake past turns: user = ticket, assistant = label. The model copies "what it answered before".</details>
<details><summary>Q3. Few-shot fixed 2 tickets. What went wrong?</summary>It broke 1 ("Where is your office located?" → login). Examples teach things you didn't mean.</details>
<details><summary>Q4. Why does step-by-step help?</summary>Each token is predicted from the ones before (2.1). Written steps become input for the next steps.</details>
<details><summary>Q5. Why take the LAST "Answer:" line?</summary>The model may correct itself: "Answer: 95 ... Wait ... Answer: 65".</details>
<details><summary>Q6. "8.00" vs expected "8": equal?</summary>As text no, as numbers yes. Compare as numbers (`Decimal` / `float`); "eight" → False.</details>
<details><summary>Q7. Is a strict system prompt a security wall?</summary>No. A ticket saying "ignore the rules" can win (prompt injection, 3.4).</details>
