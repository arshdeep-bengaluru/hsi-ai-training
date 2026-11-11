"""Helper for Squads 2, 3 and 4 while Squad 1 is still working.

Loads every kb/*.md into the "hsi_kb" collection, one chunk per paragraph, using the real
Ollama embeddings. It is NOT the solution to Squad 1 (no overlap, no word chunking).

Run from the repo root:  python scripts/seed_kb.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hsi_rag import llm, store  # noqa: E402

KB = Path(__file__).resolve().parent.parent / "kb"

ids, docs, metas = [], [], []
for f in sorted(KB.glob("*.md")):
    paras = [p.strip() for p in f.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    paras = [p for p in paras if not p.startswith("SYNTHETIC")]
    for i, p in enumerate(paras):
        cid = f"{f.name}-{i}"
        ids.append(cid)
        docs.append(p)
        metas.append({"source": f.name, "chunk_id": cid, "title": f.stem})

col = store.get_collection()
col.upsert(ids=ids, documents=docs, embeddings=llm.embed(docs), metadatas=metas)
print(f"Seeded {len(ids)} chunks into '{col.name}'.")
