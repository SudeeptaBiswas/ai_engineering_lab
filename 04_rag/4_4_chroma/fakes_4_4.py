"""Given test helpers for lesson 4.4: 3 tiny chunks, a fake embed function, an empty collection.

The fake vectors have 3 numbers, one per topic (refund, sync, price), so a test can
say exactly which chunk must come first. Real vectors have 768 (handbook_4_4.embed_texts).
"""

import uuid

import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI

from chroma_store_4_4 import NO_TELEMETRY, open_collection
from handbook_4_4 import HandbookChunk
from lab_tools.log import debug, log

REFUND_VECTOR = [1.0, 0.0, 0.0]
SYNC_VECTOR = [0.0, 1.0, 0.0]
PRICE_VECTOR = [0.0, 0.0, 1.0]
OTHER_VECTOR = [0.6, 0.0, 0.8]  # for a text with none of the 3 words; length 1.0 too

REFUND_CHUNK = HandbookChunk("refunds-0", "Refunds", 0, "Refunds\n\nAsk for a refund within 14 days.")
SYNC_CHUNK = HandbookChunk("sync-0", "Sync", 1, "Sync\n\nSync runs every 60 seconds.")
PLANS_CHUNK = HandbookChunk("plans-0", "Plans", 2, "Plans\n\nThe price of Plus is 6 euros.")
TEST_CHUNKS = [REFUND_CHUNK, SYNC_CHUNK, PLANS_CHUNK]  # in handbook order


class FakeEmbedder:
    """Stands in for Ollama: picks a vector by a word in the text, and remembers every call."""

    @debug
    def __init__(self) -> None:
        """Start with no calls."""
        self.calls: list[list[str]] = []  # the texts of each call, e.g. [["Refunds\n\n..."], [...]]
        log.debug("result: fake embedder ready")

    def __call__(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text: REFUND / SYNC / PRICE_VECTOR by the first word found, else OTHER.

        No own log lines: the code under test logs its embed calls.
        Args:
            texts: e.g. ["Refunds\\n\\nAsk for a refund within 14 days."].
        Returns:
            e.g. [[1.0, 0.0, 0.0]].
        """
        self.calls.append(texts)
        vectors: list[list[float]] = []
        for text in texts:
            lowered_text = text.lower()
            if "refund" in lowered_text:
                vectors.append(REFUND_VECTOR)
            elif "sync" in lowered_text:
                vectors.append(SYNC_VECTOR)
            elif "price" in lowered_text:
                vectors.append(PRICE_VECTOR)
            else:
                vectors.append(OTHER_VECTOR)
        return vectors


@debug
def make_empty_collection() -> tuple[ClientAPI, Collection]:
    """An empty in-memory collection with a new random name.

    Why a new name: every EphemeralClient in one Python process shares the same
    memory, so a fixed name would carry chunks from one test into the next.
    Returns:
        (client, collection); the test deletes the collection at the end.
    """
    client = chromadb.EphemeralClient(settings=NO_TELEMETRY)
    collection_name = f"test-{uuid.uuid4().hex}"  # e.g. "test-3f2a...", 32 random hex digits
    collection = open_collection(client, collection_name)
    log.debug("result: %s", collection_name)
    return client, collection
