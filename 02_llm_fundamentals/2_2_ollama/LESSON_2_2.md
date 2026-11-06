# 2.2 Ollama: models, quantization, CPU limits (~1 h)

Read this, try the commands in a terminal, run
[examples_2_2_1_size.py](examples_2_2_1_size.py) and [examples_2_2_2_speed.py](examples_2_2_2_speed.py),
then solve [exercises_2_2.py](exercises_2_2.py).
No HTTP yet — calling Ollama from Python comes in 2.3 (after httpx in 1.7).

All numbers below were **measured on 10284Sudee** (Intel i5-10210U, 4 cores,
31.8 GB RAM, no GPU), Ollama 0.40.14, on 2026-11-05.

## 1. What Ollama is
A program that downloads LLMs and runs them **on your own PC**.
Java view: like a local **database server**. It runs in the background,
listens on a port (`localhost:11434`), and your code talks to it.
Models work like **Docker images**: pull, list, remove.

| Command | Does | Docker / Java view |
|---|---|---|
| `ollama pull qwen3:4b` | download a model | `docker pull` |
| `ollama list` | models on disk + size | `docker images` |
| `ollama show qwen3:4b` | details: size, context, quantization | `docker inspect` |
| `ollama run qwen3:4b "hi"` | load + answer one prompt | `docker run` |
| `ollama ps` | models in RAM now | `docker ps` |
| `ollama rm qwen3:4b` | delete from disk | `docker rmi` |

Add `--verbose` to `run` to see timing and speed (used in section 5).

## 2. Model names
`qwen3:4b` = **family** `qwen3` + **tag** `4b`. No tag means `latest`.
`4b` = **4 billion parameters** (weights). A weight is one number the model
learned in training. More weights = knows more, but bigger and slower.

`ollama show qwen3:4b` printed (cut):
```
parameters          4.0B
context length      262144      <- max tokens it CAN see (section 2.1)
quantization        Q4_K_M      <- how each weight is stored (next section)
```

## 3. Quantization = fewer bits per weight
Each weight is a number. How many bits you store it in decides the size.
Java view: `double` (64 bits) vs `float` (32) vs `short` (16) vs `byte` (8).
Fewer bits = smaller and faster, slightly less precise.

**File size (GB) ≈ billions of weights × bits per weight ÷ 8**

| Format | Bits / weight | qwen3:4b size | Quality |
|---|---|---|---|
| FP16 | 16 | 8.0 GB | original |
| Q8_0 | 8.5 | 4.2 GB | almost same |
| Q4_K_M | ~5 | 2.5 GB (measured) | small loss — Ollama's usual default |

Rule: a **bigger model at Q4 usually beats a smaller model at FP16**.

## 4. RAM: file size is not enough
While running, the model also needs memory for the text it is reading
(the "KV cache" — grows with the context window) + overhead.
Measured: file **2.5 GB** → `ollama ps` showed **3.2 GB** (`CONTEXT 4096`, `100% CPU`).
That is +28%. This lab plans with **file size × 1.3**.

## 5. Speed on CPU
Three costs, from `ollama run qwen3:4b --verbose`:

| Step | Measured | Means |
|---|---|---|
| Load (first call only) | 9.4 s | copy the file into RAM |
| Read the prompt | ~21 tokens/s | "prompt eval rate" |
| Write the answer | ~7 tokens/s | "eval rate" — the one you feel |

Ollama keeps the model in RAM for 5 minutes after a call (`--keepalive`
changes it), so the 2nd call skips the load: 9.4 s → 0.009 s measured.

Two sizes, same family (one run each):

| Model | File | In RAM | Load | Read | Write |
|---|---|---|---|---|---|
| qwen3:4b | 2.5 GB | 3.2 GB | 9.4 s | 21 tok/s | 7.1 tok/s |
| qwen3:1.7b | 1.4 GB | 1.9 GB | 1.9 s | 63 tok/s | 15.4 tok/s |

Half the file → about **2× faster** writing. Note: the name says 1.7b,
`ollama show qwen3:1.7b` says `2.0B` — trust `show`, not the name.

Why so slow? On CPU, every new token reads **all** weights from RAM once.
Bigger file = more to read per token. A GPU has much faster memory.

## 6. Thinking models
qwen3 "thinks" before it answers: it writes hidden reasoning first,
then the answer. Better on hard questions, but every thinking token
costs the same ~7 tokens/s. Measured, prompt *"What is 2+2? Answer with one number."*:

| Way | Tokens written | Time | What you see |
|---|---|---|---|
| `--think=false` | 210 | 40 s (incl. 9.4 s load) | still thinks; the thinking text **leaks into the answer**, ends with `</think>` |
| `--think=true --hidethinking` | 236 | 33 s | only `4` — thinking hidden, **not skipped** |
| `/no_think` at the end of the prompt | 54 | 8 s | short "Thinking..." block, then `4` |

So: answer = `4`, but 99% of the tokens were thinking.
`--think=false` did not work with qwen3:4b on Ollama 0.40.14 (same on BISWAS).
`/no_think` is a qwen3 trick (written in the prompt), not an Ollama setting —
and not reliable: on qwen3:1.7b it changed nothing (185 vs 184 tokens).
We look at this again with the HTTP API in 2.3.

## 7. Try it (5 min)
```
ollama list
ollama show qwen3:1.7b
ollama run qwen3:1.7b --verbose "Name 3 colors. /no_think"
ollama ps
```
Compare `eval rate` with the table in section 5.

## 8. Exercises
[exercises_2_2.py](exercises_2_2.py): 7 small functions, 13 checks.
Model names, size math, "does it fit?", reading `--verbose` output,
time estimates, thinking share. All plain Python, no model call.
