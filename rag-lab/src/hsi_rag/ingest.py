"""SQUAD 1 - INGESTION. You own this file.

Read docs/squad-1-ingestion.md first. Your tests: tests/test_ingest.py
"""
import sys
from pathlib import Path

from . import config, llm, store  # noqa: F401  (use llm.embed and store.get_collection)


def chunk(text: str, size: int = 500, overlap: int = 60) -> list[str]:
    """Split `text` into chunks of at most `size` words.

    Consecutive chunks share `overlap` words. Empty text gives []. Text shorter than
    `size` gives one chunk. See code-along 5 in the slides.
    """
    raise NotImplementedError("Squad 1: implement chunk()")


def ingest(path: str) -> int:
    """Index every *.md file in directory `path` into the Chroma collection "hsi_kb".

    For each chunk store: id = "<file name>-<index>", the chunk text as the document,
    its embedding (llm.embed), and metadata {"source": <file name>, "chunk_id": <same as id>,
    "title": <file name without .md>}.

    Returns the number of chunks written. Running twice must NOT create duplicates
    (use the same ids and col.upsert). See code-along 6 in the slides.
    """
    raise NotImplementedError("Squad 1: implement ingest()")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "kb"
    print(f"Indexed {ingest(folder)} chunks into '{config.COLLECTION}' at {config.CHROMA_PATH}")
