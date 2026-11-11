# Architecture and contracts

```
HSI documents -> [Ingestion] -> Chroma "hsi_kb" -> [Query] -> Ollama (LLM)
                                     ^                 |
                              Ollama (embeddings)      v
                                              [API /ask] -> [Chat UI]
                                                    ^
                                             [Evals / Ops]
```

Ollama runs on the EC2 instance bound to `127.0.0.1:11434`. Developers reach it with an SSH tunnel (`ssh -L 11434:localhost:11434 <host>`). The port is never exposed to the internet.

## Models (to confirm in the load test)
- LLM: 7-8B instruct model on the GPU instance (a 3B model for CPU-only fallback).
- Embeddings: one embedding model, the same for ingest and query (e.g. `nomic-embed-text`).

## Contract 1: Ingestion
```python
def ingest(path: str) -> int:
    """Load documents under `path`, chunk, embed, upsert into Chroma collection "hsi_kb".
    Returns the number of chunks written. Re-running on the same files must not create duplicates."""
```
Chunk metadata (required): `source` (file name), `chunk_id` (stable string), `title`.

## Contract 2: Query
```python
REFUSAL = "I don't have that information. Please ask the HSI team."

def answer(question: str) -> dict:
    """Returns {"answer": str, "sources": [{"source": str, "chunk_id": str}]}.
    If the retrieved context does not contain the answer, answer == REFUSAL and sources == []."""
```

## Contract 3: API
`POST /ask` with `{"question": str}` returns `{"answer": str, "sources": [...]}`. `GET /health` returns `{"status": "ok"}`. Requests require an auth token.

## Contract 4: Evals
`tests/questions.yaml`:
```yaml
- id: Q001
  question: "..."
  type: answerable | trap | privacy
  expect_source: "returnship-faq.md"   # for answerable
  expect_contains: ["..."]             # optional
```
`evals/run.py` calls `answer()` and reports, per question: correct, cited, safe. Pass conditions: answerable questions cite `expect_source`; trap and privacy questions return exactly `REFUSAL`.

## Operational notes
- Set `OLLAMA_NUM_PARALLEL` and `OLLAMA_MAX_LOADED_MODELS` explicitly; keep the LLM and the embedding model loaded together so ingest and queries do not evict each other. Choose values from the load test, not from defaults.
- Load test covers 14 concurrent askers plus a concurrent ingest.
- One shared collection `hsi_kb`; squads use scratch collections `dev_<squad>` while building.
- The deployed assistant stays running; document owner and refresh process go in the runbook.
