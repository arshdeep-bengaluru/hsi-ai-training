"""Chroma access. Shared plumbing: do not edit."""
import chromadb

from . import config


def get_collection(name: str | None = None):
    """Return the Chroma collection (default: hsi_kb), creating it if needed.

    Uses cosine distance. Chroma returns distance, so lower means closer."""
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    return client.get_or_create_collection(
        name or config.COLLECTION, metadata={"hnsw:space": "cosine"}
    )
