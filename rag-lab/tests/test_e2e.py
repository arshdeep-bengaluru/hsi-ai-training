"""Integration checks. Do not edit.

test_wiring_* runs offline (fake model). The `integration` tests use the REAL Ollama:
    RUN_INTEGRATION=1 pytest -m integration -q        (macOS/Linux)
    $env:RUN_INTEGRATION="1"; pytest -m integration -q  (Windows PowerShell)
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evals import run as evals_run
from hsi_rag import api, ingest, llm

QPATH = Path(__file__).parent / "questions.yaml"


def test_wiring_ingest_to_api(kb_dir, monkeypatch):
    """Squad 1 -> Squad 2 -> Squad 3 work together (with a fake model)."""
    monkeypatch.setenv("HSI_API_TOKEN", "t")
    assert ingest.ingest(kb_dir) > 0
    r = TestClient(api.app).post(
        "/ask",
        json={"question": "Who can join a returnship?"},
        headers={"Authorization": "Bearer t"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["answer"]
    assert body["sources"]


@pytest.mark.integration
def test_ollama_is_reachable():
    vectors = llm.embed(["hello"])
    assert len(vectors) == 1 and len(vectors[0]) > 10
    assert isinstance(llm.chat("Reply with the single word OK."), str)


@pytest.mark.integration
def test_real_model_passes_the_whole_eval(kb_dir):
    """The final check: real model, real retrieval, all of Squad 4's questions."""
    ingest.ingest(kb_dir)
    summary = evals_run.run(str(QPATH))
    failed = [r["id"] for r in summary["results"] if not r["passed"]]
    assert not failed, f"failing questions: {failed}"
