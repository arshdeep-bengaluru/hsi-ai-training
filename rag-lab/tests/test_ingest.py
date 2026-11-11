"""Squad 1 tests. Do not edit."""
from pathlib import Path

from hsi_rag import ingest, store


def words(n):
    return " ".join(f"w{i}" for i in range(n))


def test_chunk_empty_text_gives_no_chunks():
    assert ingest.chunk("") == []


def test_chunk_short_text_is_one_chunk():
    assert ingest.chunk(words(10)) == [words(10)]


def test_chunk_respects_size_and_count():
    chunks = ingest.chunk(words(1200), size=500, overlap=60)
    assert len(chunks) == 3
    assert all(len(c.split()) <= 500 for c in chunks)


def test_chunk_overlap_is_shared_between_neighbours():
    chunks = ingest.chunk(words(1200), size=500, overlap=60)
    assert chunks[0].split()[-60:] == chunks[1].split()[:60]


def test_ingest_returns_count_and_fills_collection(kb_dir):
    n = ingest.ingest(kb_dir)
    assert n > 0
    assert store.get_collection().count() == n


def test_ingest_stores_required_metadata(kb_dir):
    ingest.ingest(kb_dir)
    got = store.get_collection().get()
    assert got["ids"]
    for chunk_id, meta in zip(got["ids"], got["metadatas"]):
        assert meta["chunk_id"] == chunk_id
        assert meta["source"]
        assert meta["title"]


def test_ingest_is_idempotent(kb_dir):
    first = ingest.ingest(kb_dir)
    second = ingest.ingest(kb_dir)
    assert first == second
    assert store.get_collection().count() == first


def test_ingest_covers_every_kb_file(kb_dir):
    ingest.ingest(kb_dir)
    sources = {m["source"] for m in store.get_collection().get()["metadatas"]}
    assert sources == {p.name for p in Path(kb_dir).glob("*.md")}
