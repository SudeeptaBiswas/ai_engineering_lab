"""Part 2 of 2: HTTP with httpx, against the real Ollama on this PC.

Needs Ollama running (it starts with Windows; check: `ollama list`).
Only fast calls: list and describe models. Generating text comes in 2.3.
"""

import httpx  # HTTP client. Java: java.net.http.HttpClient

# 127.0.0.1, not "localhost": on Windows "localhost" tries IPv6 first and
# waits 2 s per call (measured 2.16 s vs 0.02 s). Ollama listens on IPv4 only.
OLLAMA_URL = "http://127.0.0.1:11434"  # Ollama's default port

# ---------- 1. Simplest GET ----------
# Java: client.send(HttpRequest.newBuilder(uri).GET().build(), ofString())
response = httpx.get(f"{OLLAMA_URL}/api/version", timeout=10.0)  # seconds
print("status:", response.status_code)  # 200 = OK
print("raw text:", response.text)  # body as str: {"version":"0.40.14"}
print("as dict:", response.json())  # body parsed as JSON -> dict
print("version:", response.json()["version"])

# ---------- 2. A reusable client ----------
# httpx.Client keeps the connection open between calls (faster) and holds
# shared settings. `with` closes it at the end. Java: one HttpClient, reused.
with httpx.Client(base_url=OLLAMA_URL, timeout=10.0) as client:

    # GET /api/tags = list of downloaded models, like `ollama list`
    tags = client.get("/api/tags").json()  # base_url + "/api/tags"
    # tags = {"models": [{"name": "qwen3:4b", "size": 2497293931, ...}, ...]}
    print("\nmodels on this PC:")
    for model in tags["models"]:
        size_gb = model["size"] / 1_000_000_000  # bytes -> GB. "_" = readable 1e9
        print(f"  {model['name']:<11} {size_gb:.1f} GB  {model['details']['quantization_level']}")

    # ---------- 3. POST with a JSON body ----------
    # json=... turns the dict into JSON and sets Content-Type for you.
    # Java: POST(BodyPublishers.ofString(mapper.writeValueAsString(body)))
    show = client.post("/api/show", json={"model": "qwen3:4b"}).json()
    print("\nqwen3:4b details:", show["details"]["parameter_size"], show["capabilities"])

    # ---------- 4. Errors: status codes ----------
    # A 404 is NOT an exception in httpx. You check it, or call raise_for_status().
    missing = client.post("/api/show", json={"model": "no-such-model"})
    print("\nmissing model ->", missing.status_code, missing.json()["error"])
    try:
        missing.raise_for_status()  # throws for 4xx / 5xx
    except httpx.HTTPStatusError as error:
        print("raise_for_status ->", type(error).__name__, error.response.status_code)

# ---------- 5. Errors: server not running ----------
# Port 11999: nothing listens there, like Ollama being off.
# Measured on Windows: this gives ConnectTimeout (after 2 s), not ConnectError.
# Both are children of httpx.TransportError, so catch the parent.
# Java: catch (IOException e) catches all its subclasses the same way.
try:
    httpx.get("http://127.0.0.1:11999/api/version", timeout=2.0)
except httpx.TransportError as error:
    print("\nno server ->", type(error).__name__)
