"""Part 1 of 2: files and JSON. No network.

Writes only into a temporary folder that is deleted at the end.
How to read: code between "explicit start/end" is the long, step-by-step way.
The "# concise:" line right after it does the same in short Python style.
"""

import json  # JSON <-> dict/list. Java: Jackson ObjectMapper
import tempfile  # temporary folder. Java: Files.createTempDirectory
from pathlib import Path  # a file path object. Java: java.nio.file.Path

# `with` = try-with-resources: the folder is deleted when the block ends,
# even if an error happens inside.
with tempfile.TemporaryDirectory() as temp_folder_name:
    folder = Path(temp_folder_name)  # str -> Path

    # ---------- 1. Paths ----------
    # "/" joins path parts (Python overloads the operator). Java: path.resolve("notes.txt")
    notes_path = folder / "notes.txt"
    print("name:", notes_path.name, "| suffix:", notes_path.suffix)  # notes.txt | .txt

    # ---------- 2. Write and read a whole text file ----------
    # Always pass encoding="utf-8": the Windows default is not UTF-8.
    # Java: Files.writeString(path, text, UTF_8)
    notes_path.write_text("first line\nsecond line\n", encoding="utf-8")
    whole_text = notes_path.read_text(encoding="utf-8")  # Java: Files.readString
    print("exists:", notes_path.exists(), "| chars:", len(whole_text))

    # ---------- 3. Line by line (big files) ----------
    # open(...) returns a file object; `with` closes it. "a" = append mode.
    # Modes: "r" read (default), "w" write (wipes the file!), "a" append.
    with open(notes_path, "a", encoding="utf-8") as file:
        file.write("third line\n")  # write() does NOT add "\n" itself
    # --- explicit start ---
    line_count = 0
    with open(notes_path, encoding="utf-8") as file:
        for line in file:  # reads one line at a time, not the whole file
            line_count = line_count + 1
            print("  line:", line.rstrip("\n"))  # rstrip = drop the trailing "\n"
    # --- explicit end ---
    # concise: line_count = len(notes_path.read_text(encoding="utf-8").splitlines())
    print("lines:", line_count)

    # ---------- 4. JSON text <-> Python objects ----------
    # JSON object -> dict, array -> list, true/false -> True/False, null -> None
    model_info = {"name": "qwen3:4b", "size_gb": 2.5, "tags": ["thinking"], "gpu": None}
    json_text = json.dumps(model_info)  # dict -> str. Java: mapper.writeValueAsString
    print("\njson:", json_text)  # note: None became null
    back_again = json.loads(json_text)  # str -> dict. Java: mapper.readValue
    print("same after round trip:", back_again == model_info)  # == compares content

    # ---------- 5. JSON file ----------
    report_path = folder / "report.json"
    # indent=2 = pretty print, like mapper.writerWithDefaultPrettyPrinter()
    report_path.write_text(json.dumps(model_info, indent=2), encoding="utf-8")
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    print("from file:", loaded["name"], loaded["size_gb"])

    # ---------- 6. Missing file -> exception ----------
    try:
        (folder / "missing.json").read_text(encoding="utf-8")
    except FileNotFoundError as error:  # Java: NoSuchFileException
        print("\nerror:", type(error).__name__)

print("temp folder deleted:", not folder.exists())
