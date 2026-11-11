"""Shared test setup. Shared plumbing: do not edit.

By default every test runs OFFLINE: llm.embed and llm.chat are replaced by fakes, and
Chroma writes to a temporary folder. So `pytest` works on any laptop, with or without
the tunnel. Tests marked `integration` use the real Ollama (RUN_INTEGRATION=1).
"""
import hashlib
import os
import re
from pathlib import Path

import numpy as np
import pytest

from hsi_rag import config as cfg
from hsi_rag import llm, store

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "kb"
DIM = 256


def _vector(text: str) -> list[float]:
    """Deterministic bag-of-words embedding: similar words give similar vectors."""
    v = np.zeros(DIM)
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        v[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1.0
    norm = np.linalg.norm(v)
    return (v / norm if norm else v).tolist()


def fake_embed(texts):
    return [_vector(t) for t in texts]


class FakeChat:
    """Stands in for llm.chat. Set `.reply` to control what the 'model' says."""

    def __init__(self):
        self.prompts = []
        self.reply = "According to the HSI documents, see the cited source. [faq.md-0]"

    def __call__(self, prompt, temperature=0.0):
        self.prompts.append(prompt)
        return self.reply


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_INTEGRATION") == "1":
        return
    skip = pytest.mark.skip(reason="integration test: set RUN_INTEGRATION=1 (needs Ollama)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch, request):
    monkeypatch.setattr(cfg, "CHROMA_PATH", str(tmp_path / "chroma"))
    if "integration" not in request.keywords:
        monkeypatch.setattr(llm, "embed", fake_embed)


@pytest.fixture(autouse=True)
def fake_chat(monkeypatch, request):
    chat = FakeChat()
    if "integration" not in request.keywords:
        monkeypatch.setattr(llm, "chat", chat)
    return chat


@pytest.fixture
def kb_dir():
    return str(KB_DIR)


@pytest.fixture
def seeded():
    """The knowledge base loaded by test-only code, so Squads 2 to 4 do not depend on Squad 1."""
    ids, docs, metas = [], [], []
    for f in sorted(KB_DIR.glob("*.md")):
        paras = [p.strip() for p in f.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        paras = [p for p in paras if not p.startswith("SYNTHETIC")]
        for i, p in enumerate(paras):
            cid = f"{f.name}-{i}"
            ids.append(cid)
            docs.append(p)
            metas.append({"source": f.name, "chunk_id": cid, "title": f.stem})
    col = store.get_collection()
    col.upsert(ids=ids, documents=docs, embeddings=fake_embed(docs), metadatas=metas)
    return col
