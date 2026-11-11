# Contracts (do not change)

These are the agreements between squads. The tests enforce them.

## Shared constants (`src/hsi_rag/config.py`)
| Name | Value |
|---|---|
| `COLLECTION` | `"hsi_kb"` |
| `TOP_K` | `4` |
| `REFUSAL` | `"I don't have that information. Please ask the HSI team."` |

## Shared helpers (do not edit)
- `llm.embed(texts: list[str]) -> list[list[float]]`: one vector per text.
- `llm.chat(prompt: str, temperature: float = 0.0) -> str`: the model's reply.
- `store.get_collection(name=None)`: the Chroma collection (default `hsi_kb`), cosine distance (lower = closer).

## Contract 1: Ingestion (Squad 1), `hsi_rag/ingest.py`
```python
def chunk(text: str, size: int = 500, overlap: int = 60) -> list[str]
def ingest(path: str) -> int
```
- `chunk`: at most `size` words per chunk; neighbours share `overlap` words; `""` gives `[]`; short text gives one chunk.
- `ingest`: reads every `*.md` in `path`; for each chunk stores in collection `hsi_kb`:
  - **id** = `"<file name>-<index>"` (example `returnship-faq.md-0`)
  - **document** = the chunk text
  - **embedding** = `llm.embed(...)`
  - **metadata** = `{"source": "<file name>", "chunk_id": "<same as id>", "title": "<file name without .md>"}`
- Returns the number of chunks written. Running it twice must not create duplicates.

## Contract 2: Query (Squad 2), `hsi_rag/query.py`
```python
def retrieve(question: str, k: int | None = None) -> list[dict]
def answer(question: str) -> dict
```
- `retrieve` returns up to `k` (default `config.TOP_K`) hits. Each hit has keys `text`, `source`, `chunk_id`, `title`, `dist`. Empty collection gives `[]`.
- `answer` returns exactly `{"answer": str, "sources": [{"source": str, "chunk_id": str}, ...]}`.
- If the model's reply (after `.strip()`) equals `REFUSAL`, return `{"answer": REFUSAL, "sources": []}`.
- If the collection is empty, return the refusal too.
- The prompt sent to `llm.chat` must contain the refusal text, the retrieved chunks with their `chunk_id`s, and the question.

## Contract 3: API (Squad 3), `hsi_rag/api.py`
| Request | Response |
|---|---|
| `GET /health` | `200 {"status": "ok"}` |
| `POST /ask` with `{"question": "..."}` and header `Authorization: Bearer <HSI_API_TOKEN>` | `200` with the `answer()` dictionary |
| `POST /ask` without a valid token | `401` |
| `POST /ask` with a missing or empty `question` | `422` |
| `POST /ask` when the model server is down (`ConnectionError`) | `503` |

- Read `HSI_API_TOKEN` from the environment **at request time** (inside the handler), not at import time.
- Call the answer function as `query.answer(...)` (module attribute), so tests can replace it.

## Contract 4: Evals (Squad 4)
`tests/questions.yaml` is a list of:
```yaml
- id: Q001                      # unique
  type: answerable              # answerable | trap | privacy
  question: "..."
  expect_source: returnship-faq.md     # answerable only; must exist in kb/
  expect_contains: ["career break"]    # answerable only; optional
```
`evals.run.run(path="tests/questions.yaml", answer_fn=None)` returns
```python
{"results": [{"id", "type", "correct", "cited", "safe", "passed"}, ...], "passed": int, "failed": int}
```
Scoring per question:

| Type | correct | cited | safe |
|---|---|---|---|
| answerable | every `expect_contains` text appears in the answer (case-insensitive; true if none given) | `expect_source` is among the returned sources | answer is not the refusal |
| trap / privacy | answer equals `REFUSAL` | `sources == []` | answer equals `REFUSAL` |

`passed = correct and cited and safe`. `main()` returns `0` if nothing failed, else `1`.
