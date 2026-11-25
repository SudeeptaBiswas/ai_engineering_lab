"""Part 1 of 3: store the handbook in Chroma on disk, then search it. Needs Ollama + nomic-embed-text.

Run it TWICE (~6 s the first time, ~0.5 s the second):
  uv run python 04_rag/4_4_chroma/examples_4_4_1_store.py

  1. store : embed the chunks Chroma does not have yet; the 2nd run embeds none
  2. look  : what Chroma answers for one question (lists inside lists)
  3. hits  : the best 3 chunks, with heading and similarity
  4. disk  : the folder Chroma keeps; delete it to start over
"""

import time  # time.perf_counter() = a stopwatch
from pathlib import Path

import chromadb
import numpy as np
from chromadb import Collection
from chromadb.base_types import Where

from chroma_store_4_4 import NO_TELEMETRY, EmbedFunction, SearchHit, open_collection
from handbook_4_4 import HandbookChunk, embed_texts, load_handbook_chunks
from lab_tools.log import debug, log

DATABASE_FOLDER = Path(__file__).parent / "chroma_db_4_4"  # git-ignored; rebuilt from the text on any PC
COLLECTION_NAME = "handbook"
TOP_K = 3  # chunks that would go into the prompt (4.1)
SAMPLE_QUESTION = "I paid three weeks ago. Can I still get a refund?"


@debug
def store_new_chunks(collection: Collection, chunks: list[HandbookChunk], embed_function: EmbedFunction) -> int:
    """Embed and add only the chunks whose id is not stored yet, so a 2nd run costs no embedding.

    How:
        1. Ask Chroma which of our ids it has (get, include=[] = ids only).
        2. Keep the other chunks; none left -> 0.
        3. Embed them in one call; add ids, vectors, texts and {"heading", "position"}.
    Args:
        collection: e.g. open_collection(client, "handbook").
        chunks: e.g. load_handbook_chunks(), 18 chunks.
        embed_function: e.g. embed_texts.
    Returns:
        Chunks added, e.g. 18 on the first run, 0 on the next.
    """
    log.debug("start: %d chunks", len(chunks))
    wanted_ids: list[str] = []
    for chunk in chunks:
        wanted_ids.append(chunk.chunk_id)
    already_stored = collection.get(ids=wanted_ids, include=[])  # only the ids that exist come back
    stored_ids = set(already_stored["ids"])
    chunks_to_add: list[HandbookChunk] = []
    for chunk in chunks:
        if chunk.chunk_id not in stored_ids:
            chunks_to_add.append(chunk)
    if len(chunks_to_add) == 0:
        log.debug("result: 0 added")
        return 0
    texts_to_add: list[str] = []
    metadatas_to_add: list[chromadb.Metadata] = []
    ids_to_add: list[str] = []
    for chunk in chunks_to_add:
        ids_to_add.append(chunk.chunk_id)
        texts_to_add.append(chunk.text)
        metadatas_to_add.append({"heading": chunk.heading, "position": chunk.position})
    vectors_to_add = np.array(embed_function(texts_to_add), dtype=np.float32)  # Chroma's type: a float32 table
    collection.add(ids=ids_to_add, embeddings=vectors_to_add, documents=texts_to_add, metadatas=metadatas_to_add)
    log.debug("result: %d added", len(ids_to_add))
    return len(ids_to_add)


@debug
def ask_collection(collection: Collection, question_vector: list[float], top_k: int,
                   where_filter: Where | None) -> list[SearchHit]:
    """The top_k chunks nearest to one question vector, best first, as SearchHits.

    How:
        1. query with a list of ONE question vector; Chroma answers one list per question.
        2. Take list [0] of ids, texts, metadatas, distances.
        3. Cosine space: similarity = 1 - distance.
    Args:
        collection: e.g. open_collection(client, "handbook").
        question_vector: e.g. embed_texts([SAMPLE_QUESTION])[0].
        top_k: e.g. 3.
        where_filter: e.g. {"heading": "Refunds"}, or None for all chunks.
    Returns:
        e.g. [SearchHit("refunds-0", "Refunds", "Refunds\\n\\nYou can ask...", 0.70), ...].
    """
    log.debug("start: top_k=%d where=%r", top_k, where_filter)
    answers = collection.query(query_embeddings=[question_vector], n_results=top_k, where=where_filter,
                               include=["documents", "metadatas", "distances"])
    texts_per_question = answers["documents"]
    metadatas_per_question = answers["metadatas"]
    distances_per_question = answers["distances"]
    if texts_per_question is None or metadatas_per_question is None or distances_per_question is None:
        raise ValueError("asked for documents, metadatas and distances, got None")
    found_ids = answers["ids"][0]  # [0] = the answers for our one question
    found_texts = texts_per_question[0]
    found_metadatas = metadatas_per_question[0]
    found_distances = distances_per_question[0]
    hits: list[SearchHit] = []
    for hit_number in range(len(found_ids)):
        heading = str(found_metadatas[hit_number]["heading"])  # metadata values are typed str | int | ...
        similarity = 1.0 - found_distances[hit_number]
        hits.append(SearchHit(found_ids[hit_number], heading, found_texts[hit_number], similarity))
    log.debug("result: %d hits", len(hits))
    return hits


@debug
def folder_size_kilobytes(folder: Path) -> int:
    """Add up the size of every file in a folder and its subfolders.

    Args:
        folder: e.g. DATABASE_FOLDER.
    Returns:
        e.g. 1300 (kilobytes).
    """
    log.debug("start: %s", folder.name)
    total_bytes = 0
    for file_path in folder.rglob("*"):  # rglob = every file, also in subfolders
        if file_path.is_file():
            total_bytes += file_path.stat().st_size
    log.debug("result: %d bytes", total_bytes)
    return total_bytes // 1024


if __name__ == "__main__":
    print("1. store")
    start_seconds = time.perf_counter()
    disk_client = chromadb.PersistentClient(path=str(DATABASE_FOLDER), settings=NO_TELEMETRY)
    handbook_collection = open_collection(disk_client, COLLECTION_NAME)
    chunks_before = handbook_collection.count()
    added_count = store_new_chunks(handbook_collection, load_handbook_chunks(), embed_texts)
    print(f"   found {chunks_before} chunks on disk, added {added_count}, "
          f"now {handbook_collection.count()} ({time.perf_counter() - start_seconds:.2f} s)")

    print("\n2. look: what query() gives back for 1 question, top 2")
    sample_vector = embed_texts([SAMPLE_QUESTION])[0]
    raw_answers = handbook_collection.query(query_embeddings=[sample_vector], n_results=2)
    print(f"   ids       = {raw_answers['ids']}")
    print(f"   distances = {raw_answers['distances']}")

    print(f"\n3. hits for: {SAMPLE_QUESTION!r}")
    for search_hit in ask_collection(handbook_collection, sample_vector, TOP_K, None):
        first_line = search_hit.chunk_text.split("\n\n")[1][:60]  # [1] = the paragraph after the heading
        print(f"   {search_hit.similarity:.3f}  {search_hit.chunk_id:26} {first_line}...")

    print(f"\n4. disk: {DATABASE_FOLDER.name}/ holds {folder_size_kilobytes(DATABASE_FOLDER)} KB")
    print(f"   total {time.perf_counter() - start_seconds:.2f} s. Run again: 0 added, no chunk embedded.")
