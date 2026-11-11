# Review: phase 02, LLM fundamentals

Per topic: the **flow** (how the process runs), the **must-remember** points,
then a **quiz**. Click a question to see the answer. Say your answer first.
Keywords: [GLOSSARY_AI.md](GLOSSARY_AI.md).

## 2.1 How LLMs work: tokens, context window
```
text → tokenizer → token ids → model → logits (1 score per vocab token)
     → softmax (odds) → pick one → append to text → repeat until "stop"
```
- An LLM only guesses the next token. A loop makes a full answer (autoregressive).
- The model has **no memory**. Your code resends the whole chat every call.
- Everything must fit the context window: system + history + question + answer.
- Too long? Drop the oldest messages, keep the system one. Too much data? RAG.

<details><summary>Q1. How does a chatbot "remember" if the model has no memory?</summary>Your code sends the whole history again on every call. It grows each turn.</details>
<details><summary>Q2. 1 token is about how much English text?</summary>~4 characters ≈ ¾ of a word.</details>
<details><summary>Q3. Logits vs softmax?</summary>Logits = raw scores (cat 2.0, mat 1.0, rat 0.5). Softmax = odds adding up to 100% (63/23/14%).</details>
<details><summary>Q4. Why does a model hallucinate?</summary>It picks what sounds right, not what is right. Check facts.</details>

## 2.2 Ollama: models, quantization, CPU limits
```
file size (GB) ≈ billions of weights × bits per weight ÷ 8
RAM needed     ≈ file size × 1.3   (KV cache + overhead)
time           = load (first call) + read prompt + write answer
```
- `qwen3:4b` = family `qwen3` + tag `4b` (4 billion weights). Trust `ollama show`, not the name.
- Q4_K_M ≈ 5 bits: qwen3:4b is 2.5 GB on disk, 3.2 GB in RAM (measured).
- CPU is slow because each new token reads **all** weights from RAM once.
- Thinking models spend most tokens thinking: hiding it doesn't skip it.

<details><summary>Q1. qwen3:4b at FP16 vs Q4_K_M: size?</summary>8.0 GB vs 2.5 GB. A bigger model at Q4 usually beats a smaller one at FP16.</details>
<details><summary>Q2. Why is the 2nd call much faster to start?</summary>Keepalive: the model stays in RAM 5 min. Load 9.4 s → 0.009 s.</details>
<details><summary>Q3. Which speed do you feel: prompt eval or eval rate?</summary>Eval rate (writing): qwen3:4b ~7 tok/s, 1.7b ~15 tok/s.</details>
<details><summary>Q4. Half the file size gives roughly what speed-up?</summary>About 2× faster writing (2.5 GB → 1.4 GB: 7.1 → 15.4 tok/s).</details>

## 2.3 Chat API over HTTP: roles, streaming
```
messages [system, user, assistant, user ...]
  → POST /api/chat {model, messages, stream, think, options}
  → reply["message"]["content"]  (+ done_reason, eval_count, durations in ns)
```
- Roles: `system` = your rules, `user` = the person, `assistant` = earlier answers.
- Always `"think": False` for qwen3:1.7b: thinking tokens eat `num_predict`.
- Streaming = NDJSON lines; the last has `done: true` + stats. Same total time.

<details><summary>Q1. done_reason "length" means?</summary>The answer hit num_predict and was cut off.</details>
<details><summary>Q2. Why was content empty with num_predict 60 and no think flag?</summary>All 60 tokens went to hidden thinking.</details>
<details><summary>Q3. Why stream if the total time is the same?</summary>First text after 0.13–0.64 s instead of 2.0–3.2 s: the user reads while it writes.</details>
<details><summary>Q4. httpx.post without "stream": False — what breaks?</summary>You get many JSON lines in one body; .json() fails with "Extra data".</details>

## 2.4 Sampling: temperature, top_k, top_p, seed
```
logits → ÷ temperature → softmax → cut tail (top_k, top_p) → weighted random pick (seed)
```
- Temperature reshapes the odds: low = safe and repeating, high = bold.
- top_k / top_p remove junk tokens **before** the pick.
- Seed makes randomness repeatable: tests stop being flaky.
- `num_predict` is a hard cut, not "be short". To get short answers, ask in the prompt.

<details><summary>Q1. T = 0 in Ollama?</summary>Acts greedy: same answer 10/10.</details>
<details><summary>Q2. top_p 0.8 on cat 0.63, mat 0.23, rat 0.14 keeps?</summary>cat + mat (0.63 → 0.86 ≥ 0.8, stop).</details>
<details><summary>Q3. qwen3 defaults when you send nothing?</summary>temperature 0.6, top_k 20, top_p 0.95.</details>
<details><summary>Q4. T for JSON output, tool calls, LLM judge?</summary>0. One "creative" token breaks parsing or the score.</details>
<details><summary>Q5. Answers too samey: change T first?</summary>No, fix the prompt first. The prompt sets the odds, T only reshapes them.</details>

## 2.5 Embeddings + similarity
```
notes + query → POST /api/embed (one batched call) → vectors (768 numbers each)
  → cosine(query, each note) → sort best first → keep top k
cosine(a, b) = dot(a, b) / (norm(a) × norm(b))
```
- Similar meaning = arrows pointing the same way.
- Divide by the norms so length doesn't count (dot 0.74 vs 7.40, cosine 1.00 for both).
- Use the **same model** for notes and query, or scores are nonsense (no error).

<details><summary>Q1. Cosine 1, 0, -1 mean?</summary>Same direction, right angle (unrelated), opposite.</details>
<details><summary>Q2. Is "unrelated" a score of 0 with real embeddings?</summary>No, ~0.3–0.45 (cat vs invoice 0.40). Compare scores, never hard-code "0.5 = match".</details>
<details><summary>Q3. "I love this movie" vs "I hate this movie" scores 0.69. Why?</summary>Embeddings measure what it's about, not whether it's positive or true.</details>
<details><summary>Q4. Why can cosine = dot for nomic-embed-text?</summary>Its vectors are normalized (length 1.0).</details>
<details><summary>Q5. Why batch the embed call?</summary>5 notes: 1 call 0.38–0.60 s vs 5 calls 1.34–1.92 s.</details>

## 2.6 Project: assistant v1, CLI chatbot with memory
```
you type → memory.add("user") → trim oldest if over budget
  → stream_chat(system + history) → print each chunk as it arrives
  → memory.add("assistant", full reply) → next turn resends it all
```
- The model remembers nothing: **memory = your code resends the history**.
- Over `num_ctx` (4096 here) Ollama drops messages silently: "Blue" instead of "green".
- So the app trims itself (oldest first, never the system message or the newest).
- `yield` hands out chunks while they arrive, so printing starts at once.

<details><summary>Q1. Where does the chatbot's memory live?</summary>In `ChatMemory.history`, a list in RAM. Every turn sends system message + history again.</details>
<details><summary>Q2. Why trim before Ollama does?</summary>Ollama cuts with no error and may drop the fact you need. Own trim = known rule: oldest first.</details>
<details><summary>Q3. Budget is 2000 but `num_ctx` is 4096. Why so low?</summary>chars / 4 is 1.2–2.2x under the real count, and the 300-token answer needs room too.</details>
<details><summary>Q4. What does calling a function with `yield` do?</summary>Runs nothing; returns a generator. Each `for` step runs to the next `yield`. One pass only.</details>
<details><summary>Q5. Why is the last stream line skipped?</summary>Its content is "" (`done: true`); "" is not a chunk (the 2.3 bug).</details>
<details><summary>Q6. How is this done at work?</summary>A library: LangChain message history + `trim_messages` (4.5), LangGraph checkpointers (6.5). Same steps inside.</details>
