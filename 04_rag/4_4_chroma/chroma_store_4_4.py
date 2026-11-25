"""Lesson 4.4 exercises: store chunks in Chroma once, search them many times. YOU fill the 5 functions.

Goal: embed each chunk only once, keep the vectors on disk, and search with a question
vector, optionally inside one section. No Ollama needed for the tests here: they pass
small made-up vectors (3 numbers) and a fake embed function that counts its calls.
Fill the functions that raise NotImplementedError until every test in this folder passes:
  uv run pytest 04_rag/4_4_chroma -v          (Ollama off? add -m "not ollama")
Start with exercises_4_4_1_store.py, then exercises_4_4_2_search.py.
The settings, SearchHit, EmbedFunction and open_collection are given; don't change them.
Style: docs/CODE_STYLE.md.
"""
# lesson-rules: user-code  (style problems here are shown as warnings, never block a commit)

from collections.abc import Callable
from dataclasses import dataclass

import chromadb  # pyright: ignore[reportUnusedImport]  (chromadb.Metadata in add_missing_chunks)
import numpy as np  # pyright: ignore[reportUnusedImport]  (used once add_missing_chunks is filled)
from chromadb import Collection
from chromadb.api import ClientAPI
from chromadb.config import Settings

from handbook_4_4 import HandbookChunk
from lab_tools.log import cut_text, debug, log  # pyright: ignore[reportUnusedImport]  (cut_text: long text in a log)

DISTANCE_SPACE = "cosine"  # how Chroma measures "far apart"; its default is "l2" (LESSON section 4)
NO_TELEMETRY = Settings(anonymized_telemetry=False)  # default True; empty in 1.5.9, older versions sent usage stats

EmbedFunction = Callable[[list[str]], list[list[float]]]  # texts in, one vector per text out


@dataclass
class SearchHit:
    """One chunk that search found, with how close it is to the question."""

    chunk_id: str  # e.g. "refunds-0"
    heading: str  # e.g. "Refunds"
    chunk_text: str  # e.g. "Refunds\n\nYou can ask for a full refund within 14 days..."
    similarity: float  # cosine similarity, 1.0 = same direction, e.g. 0.71


@debug
def open_collection(client: ClientAPI, collection_name: str) -> Collection:
    """Given: open a collection (a named table of chunks), or create it, measured by cosine.

    Args:
        client: chromadb.PersistentClient(path=..., settings=NO_TELEMETRY) for disk,
            chromadb.EphemeralClient(settings=NO_TELEMETRY) for memory only (tests).
        collection_name: 3-512 letters, digits, ".", "_" or "-", e.g. "handbook".
    Returns:
        The collection; it may already hold chunks from an earlier run.
    """
    log.debug("start: %s", collection_name)
    collection = client.get_or_create_collection(collection_name,
                                                 configuration={"hnsw": {"space": DISTANCE_SPACE}})
    log.debug("result: %d chunks inside", collection.count())
    return collection


@debug
def distance_to_similarity(distance: float, distance_space: str) -> float:
    """Turn Chroma's distance (0 = same, bigger = further) back into the similarity of 2.5.

    How:
        1. "cosine": Chroma gives 1 - similarity, so similarity = 1 - distance.
        2. "l2": Chroma gives the squared straight-line distance. For vectors of
           length 1.0 that is 2 - 2 * similarity, so similarity = 1 - distance / 2.
        3. Any other space -> ValueError.
    Args:
        distance: e.g. 0.29.
        distance_space: "cosine" or "l2".
    Returns:
        e.g. 0.71 for (0.29, "cosine"), 0.71 for (0.58, "l2").
    Raises:
        ValueError: distance_space is not "cosine" or "l2".
    """
    raise NotImplementedError("Lesson 4.4, exercise 1: distance_to_similarity")


@debug
def find_missing_ids(collection: Collection, chunk_ids: list[str]) -> list[str]:
    """Find which chunk ids the collection does not hold yet, so only those get embedded.

    How:
        1. Ask the collection for these ids with collection.get(ids=..., include=[]):
           it returns only the ids it has (include=[] = no text, no vectors: faster).
        2. Keep the ids from chunk_ids that did not come back, in their order.
    Args:
        collection: e.g. open_collection(client, "handbook").
        chunk_ids: e.g. ["refunds-0", "sync-0"].
    Returns:
        e.g. ["sync-0"] when only "refunds-0" is stored; [] when all are.
    """
    raise NotImplementedError("Lesson 4.4, exercise 2: find_missing_ids")


@debug
def add_missing_chunks(collection: Collection, chunks: list[HandbookChunk], embed_function: EmbedFunction) -> int:
    """Store the chunks the collection does not have yet: embed them once, never twice.

    How:
        1. find_missing_ids for the chunk ids. None missing -> return 0, no embed call.
        2. Keep the missing chunks, in order.
        3. One embed_function call for all their texts.
        4. collection.add with ids, embeddings, documents (the texts) and
           metadatas: {"heading": ..., "position": ...} per chunk.
           Types Chroma wants (pyright checks them): the vectors as a numpy table,
           np.array(vectors, dtype=np.float32); the metadata list as list[chromadb.Metadata].
    Args:
        collection: e.g. open_collection(client, "handbook").
        chunks: e.g. load_handbook_chunks(), 18 chunks.
        embed_function: e.g. embed_texts (Ollama), or a fake one in tests.
    Returns:
        How many chunks were added, e.g. 18 the first time, 0 the next time.
    """
    raise NotImplementedError("Lesson 4.4, exercise 3: add_missing_chunks")


@debug
def search_chunks(collection: Collection, question_vector: list[float], top_k: int,
                  heading_filter: str | None) -> list[SearchHit]:
    """Find the top_k chunks closest to a question, optionally only in one section.

    How:
        1. collection.query with query_embeddings=[question_vector] (a list of ONE question),
           n_results=top_k, include=["documents", "metadatas", "distances"].
        2. heading_filter given -> add where={"heading": heading_filter}.
        3. Chroma answers one list per question: take [0] of ids, documents, metadatas, distances.
           documents, metadatas and distances may be None to pyright: raise ValueError if so.
        4. One SearchHit per chunk, best first; similarity = distance_to_similarity(distance,
           DISTANCE_SPACE). The heading comes back typed as str | int | ...: wrap it in str(...).
    Args:
        collection: e.g. open_collection(client, "handbook").
        question_vector: e.g. embed_texts(["Can I get a refund?"])[0].
        top_k: e.g. 3.
        heading_filter: e.g. "Refunds", or None to search all chunks.
    Returns:
        e.g. [SearchHit("refunds-0", "Refunds", "Refunds\\n\\nYou can ask...", 0.71), ...];
        [] when nothing matches the filter.
    """
    raise NotImplementedError("Lesson 4.4, exercise 4: search_chunks")


@debug
def replace_chunk_text(collection: Collection, chunk_id: str, new_text: str, embed_function: EmbedFunction) -> None:
    """Change one stored chunk (text + vector), keep its heading; fail loudly if it is not there.

    How:
        1. find_missing_ids(collection, [chunk_id]) not empty -> KeyError (Chroma's update would
           silently do nothing for an unknown id).
        2. Embed new_text (one embed_function call).
        3. collection.update with ids, embeddings (np.array(..., dtype=np.float32), as in
           add_missing_chunks) and documents. Metadata left out = metadata kept.
    Args:
        collection: e.g. open_collection(client, "handbook").
        chunk_id: e.g. "refunds-0".
        new_text: e.g. "Refunds\\n\\nYou can ask for a full refund within 30 days...".
        embed_function: e.g. embed_texts.
    Raises:
        KeyError: no chunk with this id.
    """
    raise NotImplementedError("Lesson 4.4, exercise 5: replace_chunk_text")
