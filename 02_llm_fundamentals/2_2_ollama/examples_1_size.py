"""Part 1 of 2: how big is a model? Disk size and RAM, from 2 numbers.

Pure Python math, no model call. Run it, then compare with `ollama list`
and `ollama ps` on your PC.
How to read: code between "explicit start/end" is the long, step-by-step way.
The "# concise:" line right after it does the same in short Python style.
"""

# ---------- 1. A model file = a huge list of numbers (weights) ----------
# "4b" in "qwen3:4b" = 4 billion weights. Each weight is one number.
# Bits per weight decide the file size. Java view:
#   double = 64 bits, float = 32 bits, short = 16 bits, byte = 8 bits.
# Fewer bits = smaller file, a bit less precise. That is quantization.
BITS_PER_WEIGHT: dict[str, float] = {
    "FP16": 16,  # full size: how models are trained and shared
    "Q8_0": 8.5,  # 8-bit: almost no quality loss
    "Q4_K_M": 5.0,  # Ollama's usual default. ~5 bits = measured for qwen3:4b
}


def size_gb(params_billion: float, bits: float) -> float:
    """File size in GB = weights x bits / 8 (8 bits = 1 byte)."""
    # 4.0 billion weights x 5 bits = 20 billion bits = 2.5 billion bytes.
    # Billions cancel out: 4.0 x 5 / 8 = 2.5 -> 2.5 GB.
    return round(params_billion * bits / 8, 1)  # round(x, 1) = 1 decimal


# ---------- 2. Same model, three sizes ----------
# :<7 = pad to 7 chars, left aligned (like String.format("%-7s") in Java)
print("qwen3:4b (4.0 billion weights) at different quantization:")
for quant_name, bits in BITS_PER_WEIGHT.items():
    print(f"  {quant_name:<7} {bits:>4} bits -> {size_gb(4.0, bits):>4} GB")
# Measured: `ollama list` shows qwen3:4b = 2.5 GB, `ollama show` says Q4_K_M.


# ---------- 3. RAM while running = file + working memory ----------
# The model also needs memory for the conversation it is reading
# (the "KV cache", grows with the context window) + some overhead.
# Measured on 10284Sudee: file 2.5 GB, `ollama ps` = 3.2 GB at 4096 context.
FILE_GB = 2.5
LOADED_GB = 3.2
extra_percent = (LOADED_GB - FILE_GB) / FILE_GB * 100
print(f"\nloaded vs file: +{extra_percent:.0f}% extra")  # .0f = no decimals
# Rule of thumb used in this lab: plan for file size x 1.3.


# ---------- 4. Which models fit in my RAM? ----------
FREE_RAM_GB = 16.0  # pretend: half of a 32 GB PC is free
# Estimates from the formula. Real qwen3:1.7b file = 1.4 GB: `ollama show`
# says 2.0B weights (not 1.7), and small models lose more to overhead.
MODEL_SIZES_GB: dict[str, float] = {
    "qwen3:1.7b": size_gb(2.0, 5.0),
    "qwen3:4b": size_gb(4.0, 5.0),
    "qwen3:8b": size_gb(8.0, 5.0),
    "qwen3:32b": size_gb(32.0, 5.0),
}
print(f"\nfree RAM {FREE_RAM_GB} GB:")
for model_name, file_gb in MODEL_SIZES_GB.items():
    # --- explicit start ---
    if file_gb * 1.3 <= FREE_RAM_GB:
        verdict = "fits"
    else:
        verdict = "too big"
    # --- explicit end ---
    # concise: verdict = "fits" if file_gb * 1.3 <= FREE_RAM_GB else "too big"
    print(f"  {model_name:<11} {file_gb:>5} GB -> {verdict}")
# Fits in RAM is not the same as fast: next file shows speed.
