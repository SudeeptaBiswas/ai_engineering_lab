# Glossary: AI / LLM keywords

A–Z. One line each. Numbers are measured in the lessons (10284Sudee / BISWAS,
CPU only). Topic = where it was taught; open that LESSON for the full story.
Process + quiz: [REVIEW_02_llm.md](REVIEW_02_llm.md), [REVIEW_03_prompting.md](REVIEW_03_prompting.md) (3.1–3.4).

| Term | Plain meaning | Example / number | Topic |
|---|---|---|---|
| `/api/chat` | Ollama endpoint: messages in, answer out | `reply["message"]["content"]` | 2.3 |
| `/api/embed` | Ollama endpoint: texts in, vectors out | `{"model": ..., "input": [texts]}` | 2.5 |
| Assistant (role) | the model's earlier answers in the history | `{"role": "assistant", ...}` | 2.3 |
| Autoregressive | write one token, append it, guess the next, repeat | "The cat" → "sat" → "on" ... | 2.1 |
| Batching | send many texts in one call | 5 notes: 1 call 0.38–0.60 s vs 5 calls 1.34–1.92 s | 2.5 |
| BPE | build tokens by gluing the most common neighbour pair, again and again | `t`+`h` → `th` | 2.1 |
| Chat memory | the history your code keeps and resends every turn | `ChatMemory.messages()` | 2.6 |
| Code gate | code checks every tool call before it runs: who asked, how much | refund(500) blocked; "needs a human" | 3.4 |
| Constrained decoding | the server only lets the model write tokens that fit a schema | `"format": schema` → 8/8 replies parse | 3.2 |
| Context length | max tokens a model CAN see | qwen3:4b: 262 144 | 2.2 |
| Context window | token limit for one call: system + history + question + answer | like max request body size | 2.1 |
| Cosine similarity | how alike two directions are: dot ÷ (norm × norm) | 1 same, 0 right angle, -1 opposite | 2.5 |
| Dimensions | how many numbers in one embedding | nomic-embed-text: 768 | 2.5 |
| `done_reason` | why the answer ended | `"stop"` finished, `"length"` cut by num_predict | 2.3 |
| Dot product | multiply pair by pair, add up | [1,2,3]·[4,5,6] = 32 | 2.5 |
| Embedding | text turned into numbers by meaning | "cat" → [0.05, 0.06, ...] | 2.5 |
| Embedding model | a model that only embeds; a chat model can't | qwen3:1.7b on /api/embed → HTTP 501 | 2.5 |
| `eval_count` | tokens the model wrote | `prompt_eval_count` = tokens read | 2.3 |
| Eval rate | writing speed, the one you feel | qwen3:4b 7.1 tok/s, 1.7b 15.4 tok/s | 2.2 |
| Few-shot | solved examples sent as past user/assistant turns | 4 shots: 6/8 → 7/8, 2.5x prompt tokens | 3.1 |
| Flaky test | passes on some runs, fails on others | fix: seed, or T 0 | 2.4 |
| `format` (Ollama) | `"json"` or a JSON Schema dict in the /api/chat body | `Triage.model_json_schema()` | 3.2 |
| FP16 / Q8_0 / Q4_K_M | quantization formats: 16 / 8.5 / ~5 bits per weight | qwen3:4b: 8.0 / 4.2 / 2.5 GB | 2.2 |
| Greedy | always pick the top token | T 0 → same answer 10/10 | 2.1, 2.4 |
| Hallucination | picks what sounds right, not what is right | "Blue." with no history (2.3) | 2.1 |
| Instruction tuning | training on (question, good answer) pairs | step 2 of 3 | 2.1 |
| JSON Schema | a JSON description of a JSON shape: types, `enum`, `minimum`, `maxLength`, `required` | made from a pydantic model | 3.2 |
| Keepalive | Ollama keeps a model in RAM after a call | 5 min; 2nd call load 9.4 s → 0.009 s | 2.2 |
| KV cache | memory for the text being read; grows with context | why RAM ≈ file × 1.3 | 2.2 |
| Least privilege | give the model only the tools the task needs, read-only where you can | order_status yes, delete_order no | 3.4 |
| Load time | copy the model file into RAM (first call) | qwen3:4b 9.4 s, 1.7b 1.9 s | 2.2 |
| Logits | raw score the model gives every vocabulary token | cat 2.0, mat 1.0, rat 0.5 | 2.1 |
| LLM | a next-token guesser, run in a loop | IntelliJ autocomplete for any text | 2.1 |
| Messages | the chat: a list of {role, content} | system, user, assistant | 2.3 |
| NDJSON | one JSON object per line (streaming format) | last line has `done: true` + stats | 2.3 |
| No memory (stateless) | every call starts from zero; your code resends history | like a stateless REST call | 2.1, 2.3 |
| Norm | arrow length: sqrt(dot(a, a)) | norm([3, 4]) = 5 | 2.5 |
| Normalized vector | length 1.0, so cosine = dot | nomic vectors are | 2.5 |
| `num_ctx` | Ollama option: context size in tokens; over it, messages are dropped silently | default 4096 here; 1024 gave "Blue" | 2.6 |
| `num_predict` | max tokens to write: a hard cut, not "be short" | 12 → stops mid-sentence | 2.3, 2.4 |
| Ollama | runs LLMs on your PC, port 11434 | pull/list/show/run/ps/rm ≈ Docker | 2.2 |
| Output parsing | code checks the reply's shape; never trust it | "**bug**" → bug; a sentence → None | 3.1 |
| Parameters (weights) | numbers the model learned | 4b = 4 billion | 2.2 |
| Pre-training | read huge text, learn to guess the next piece | step 1 of 3 | 2.1 |
| Preference tuning | people rank answers, model learns what they like | step 3 of 3 | 2.1 |
| Prompt eval rate | reading speed | qwen3:4b ~21 tok/s, 1.7b 63 tok/s | 2.2 |
| Prompt injection | untrusted text the model follows as your orders; direct (user) or indirect (in data) | ticket attacks hijacked 6/6 | 3.4 |
| Prompt pattern | a known way to write messages so the answer comes back in the shape you need | system rules, few-shot, step-by-step | 3.1 |
| Quantization | store each weight in fewer bits: smaller, faster, a bit less precise | GB ≈ billions × bits ÷ 8 | 2.2 |
| RAG | find the useful text first, send only that to the model | phase 04 | 2.1, 2.5 |
| Retry with feedback | send the bad reply + the error list back, ask again | 7/8 valid by try 2, but 2/8 right | 3.2 |
| Sampling | weighted random pick of the next token | like a loot table | 2.4 |
| Score (accuracy) | share of answers equal to the expected ones | 7 of 8 right = 0.875 | 3.1 |
| Secret leak | the model gives out what its prompt holds; check answers letters-only | SAVE-7731 leaked 4/5 | 3.4 |
| Seed | fixes the randomness: same seed + settings + prompt → same answer | `"seed": 42` → Fizzluff x5 | 2.4 |
| Semantic search | find text by meaning: embed, cosine, sort, top k | login query → reset-password note 0.68 | 2.5 |
| Softmax | turns scores into odds that add up to 100% | 2.0/1.0/0.5 → 63/23/14% | 2.1 |
| Step-by-step (chain of thought) | ask for the steps, then a fixed last line `Answer: <n>` | maths 5/6 → 6/6; 49.6 s vs 31.4 s | 3.1 |
| Streaming | get the answer in pieces as it is written | first text 0.13–0.64 s, whole 2.0–3.2 s | 2.3 |
| Structured output | the reply has a fixed shape code can check and use | Triage: label, priority, summary | 3.2 |
| System (role) | developer's rules for the whole chat | "Answer in one short sentence." | 2.3 |
| Tag (model) | the part after `:` in a model name | `qwen3:4b`; no tag = `latest` | 2.2 |
| Temperature | score ÷ T before softmax: low = safe, high = bold | qwen3 default 0.6; JSON/tools 0 | 2.4 |
| Thinking model | writes hidden reasoning before the answer | 99% of tokens for "2+2"; send `think: False` | 2.2, 2.3 |
| Token | a piece of text the model reads, as an id | 1 token ≈ 4 chars ≈ ¾ word | 2.1 |
| Tokenizer | cuts text into tokens | like a compiler's lexer | 2.1 |
| Tool calling | the model asks your code to run a named function with JSON arguments | `multiply(4821, 3967)`: 5/5 vs 2/5 alone | 3.3 |
| Tool description | all the model knows about a tool: description + args schema | no example id → not called | 3.3 |
| Tool loop | POST, run the calls, send results, POST again until a plain answer; max N rounds | 7/8 right, 30.1–34.8 s | 3.3 |
| Tool result (role) | `{"role": "tool", "tool_name": ..., "content": ...}`, one per call | errors go back as "error: ..." text | 3.3 |
| top_k | keep only the k best tokens before the pick | qwen3 default 20; `top_k 1` = greedy | 2.4 |
| top_p | keep the best tokens until they cover p | qwen3 default 0.95 | 2.4 |
| Trimming | drop the oldest messages to stay under a token budget | budget 2000, system message always kept | 2.6 |
| Untrusted text | any text you didn't write: tickets, tool results, PDFs, web pages | treat as data, never orders | 3.4 |
| User (role) | the person's messages | "What is RAG?" | 2.3 |
| Vector | a list of numbers = an arrow with a direction | [0.9, 0.1] points east | 2.5 |
| Vocabulary | all tokens a model knows (a Map<String, Integer>) | qwen3: 151 936 tokens | 2.1, 2.4 |
| Zero-shot | just the question, no rules, no examples | tickets: 0/8 usable labels | 3.1 |
