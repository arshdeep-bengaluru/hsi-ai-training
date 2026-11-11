# Table of Contents (v4): full-day developer workshop

**Goal:** 14 developers learn the concepts, then build and deploy a private RAG assistant for Her Second Innings (HSI).
**Audience:** developers (Python). RAG concepts are taught from scratch.
**Format:** full day (09:00 to 17:30). Each layer follows the same pattern: concept, then instructor code-along, then (after lunch) squad build.
**Infra:** one shared AWS EC2 GPU instance running Ollama (LLM + embeddings); developers reach it through an SSH tunnel. It stays running after the session.
**Content:** synthetic HSI-style knowledge base for the workshop; real documents are swapped in before go-live.
**Contracts:** see `ARCHITECTURE.md`.

## Agenda
| Time | # | Module | Concepts | Code-along |
|---|---|---|---|---|
| 09:00 | 0 | Context, architecture, squads (30 min) | System, contracts | none |
| 09:30 | 1 | LLMs and Ollama (45 min) | Tokens, context window, temperature, hallucination, why RAG | Call the local model; environment check |
| 10:15 | 2 | Embeddings and vector store (45 min) | Embeddings, similarity, Chroma records | Embed and compare; add and query Chroma |
| 11:00 | | Break (15 min) | | |
| 11:15 | 3 | Chunking and ingestion (45 min) | Why chunk, trade-offs, stable ids | `chunk()` and `ingest()` |
| 12:00 | 4 | Retrieval and grounded answering (45 min) | Top-k, grounded prompt, refusal, citations, debugging | `retrieve()` and `answer()` |
| 12:45 | | Lunch (45 min) | | |
| 13:30 | 5 | Serving and evals (30 min) | API and auth, eval types | `/ask` endpoint; eval loop |
| 14:00 | 6 | Squad build (90 min) | Squad contracts and rules | Squads build for real |
| 15:30 | | Break (15 min) | | |
| 15:45 | 7 | Integration and evals (45 min) | Triage: retrieval, prompt or data | Fix the worst failures |
| 16:30 | 8 | Concurrency, load test, deploy (30 min) | Parallelism, model loading | Load test; service setup |
| 17:00 | 9 | Hand-over and retro (30 min) | Ownership, runbook | none |

## After the workshop (offline)
- **Take-home task: hybrid search** (BM25 plus vector search with reciprocal rank fusion). Brief in `docs/take-home-hybrid-search.md`.
- Module 4 includes a 5-minute "RAG variants" slide (naive, hybrid, conversational, agentic, graph) so developers know what the take-home leads toward.
- A later session (for example a Nasscom community course on RAG architecture) can cover the variants in depth.

## Squads (3 to 4 people each)
| Squad | Owns | Contract |
|---|---|---|
| 1. Ingestion | Load, chunk, embed, store | `ingest(path)` writes collection `hsi_kb` |
| 2. Query | Retrieve, prompt, cite, refuse | `answer(question)` returns answer plus sources |
| 3. API and UI | FastAPI service, chat UI, auth | `POST /ask` |
| 4. Evals and Ops | Test set, scorer, load test, logging | `tests/questions.yaml` and `evals/run.py` |

## Teaching pattern per layer
1. **Concept** (diagram, plain explanation, common mistakes).
2. **Code-along** (instructor writes 10 to 20 lines live; everyone types along against the shared Ollama).
3. **Squad build** applies the same ideas to the real contracts.

## Facilitator prep (before the session)
- Repo skeleton: stubs and failing tests per squad, plus one end-to-end test.
- Reference implementation (answer key) on a separate branch that passes the eval; code-along snippets tested against it.
- EC2 instance sized and tested, models pre-pulled, G-family quota confirmed.
- A second helper for the code-along and the squad build.

## Open items
- Where do 14 developers push code (private GitHub org or repo)?
- Real HSI documents: who supplies them and owns updates?
- How do HSI staff sign in to the deployed UI (not only an IP allow-list)?
- Region, g4dn price and G-family quota check.
- Who facilitates, and who is the second helper? Session date?
- Official NASSCOM brand kit (slides currently use colors taken from nasscom.in).
