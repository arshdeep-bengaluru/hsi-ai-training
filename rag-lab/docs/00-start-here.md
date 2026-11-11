# Start here: how this lab works

Read this once. It takes 5 minutes and saves an hour.

## The idea in four sentences
1. We keep HSI's documents in `kb/` and cut them into small **chunks**.
2. Each chunk is turned into a list of numbers (an **embedding**) and stored in a **vector store** (Chroma) with its source name.
3. When someone asks a question, we embed the question, fetch the **nearest chunks**, and give them to the language model inside a strict **prompt**.
4. The model must answer only from those chunks and cite them, or reply with one fixed **refusal sentence**.

## Who does what
| Squad | Part | Input | Output |
|---|---|---|---|
| 1 Ingestion | `ingest()` | folder of `.md` files | chunks stored in collection `hsi_kb` |
| 2 Query | `answer()` | a question | `{"answer", "sources"}` |
| 3 API and UI | `/ask` | HTTP request | same dictionary as JSON; a chat page |
| 4 Evals and Ops | `evals.run` | `tests/questions.yaml` | PASS/FAIL per question; load numbers |

The exact shapes are in `docs/contracts.md`. Learn yours and know your neighbours'.

## How the tests work (important)
- `pytest` runs **offline**. `tests/conftest.py` replaces `llm.embed` and `llm.chat` with fakes and uses a temporary database. You do not need the tunnel to run tests.
- A test going **red to green** is how you know your part meets the contract.
- Squads 2, 3 and 4 do not wait for Squad 1: a test fixture (`seeded`) loads the knowledge base for them.
- `integration` tests use the **real** model. They are skipped by default and used at the integration checkpoint.

## Using the real model (the tunnel)
Your code reaches Ollama on the server through an SSH tunnel on `localhost:11434`.
```
ssh -L 11434:localhost:11434 <user>@<ec2-host>
```
Keep that terminal open. Without it, real calls fail with a connection error (your tests still pass because they are offline).

Settings come from environment variables (defaults are fine for the workshop; see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | where the tunnel ends |
| `LLM_MODEL` | `qwen2.5:7b` | answering model |
| `EMBED_MODEL` | `nomic-embed-text` | embedding model |
| `CHROMA_PATH` | `chroma_db` | where your local database is stored |
| `HSI_API_TOKEN` | (none) | password for the API |

Set one (macOS/Linux): `export HSI_API_TOKEN=dev-token`
Set one (PowerShell): `$env:HSI_API_TOKEN = "dev-token"`

## Your local database
`python -m hsi_rag.ingest kb` (Squad 1) or `python scripts/seed_kb.py` (a quick helper) writes the knowledge base into a **local** folder `chroma_db/` on your machine. It is yours alone. The shared, deployed database is built on the server at the end of the day, with the same command.

## Rules that prevent most problems
1. **Only edit your files.** If you think someone else's file has a bug, tell them.
2. **Keep the contracts.** If you change a return shape, other squads break.
3. **`llm.embed(...)` and `llm.chat(...)`, always written that way.** Not `from hsi_rag.llm import embed`.
4. **Read settings at call time:** `config.TOP_K`, `config.REFUSAL`, not copies saved in your own variables at import time.
5. **The refusal text is a constant.** Always use `config.REFUSAL` (it is also available as `query.REFUSAL`). Never retype it.
6. **Do not commit** `.venv/`, `chroma_db/` or secrets.

## A good rhythm
1. Read your squad file top to bottom.
2. Run your tests: see them fail.
3. Do step 1, run the tests, do step 2, run the tests. Small steps.
4. When your tests are green, try it for real against the model.
5. Commit and push often.
6. Look at the stretch goals only after everything is green.

## Time plan for the build block
| Time | What |
|---|---|
| 0 to 60 min | Get your tests green |
| 60 to 75 min | Try it with the real model; fix what you see |
| 75 to 90 min | Stretch goals; get ready for the integration checkpoint |
