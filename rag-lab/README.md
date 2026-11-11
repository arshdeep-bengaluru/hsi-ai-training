# HSI RAG Lab

You are building a **private question-answering assistant for Her Second Innings (HSI)**. It answers from HSI's own documents, shows its sources, and says "I don't have that information" when the answer is not in the documents.

Today the team builds it together as **four squads**. Each squad owns one part. The parts fit together through fixed **contracts**, so you can work in parallel.

```
kb/*.md --> [1 Ingestion] --> Chroma "hsi_kb" --> [2 Query] --> Ollama (LLM)
                                                       ^
                          [3 API + Chat UI] -----------+
                          [4 Evals + Load test] -------+
```

## Start here (about 15 minutes)

Do these steps **in order**. Do not skip the checks.

### 1. Get the code
```
git clone https://github.com/arshdeep-bengaluru/hsi-ai-training.git
cd hsi-ai-training/rag-lab
```

### 2. Create a Python environment and install
macOS / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Windows (PowerShell):
```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Check: `python -c "import chromadb, ollama, fastapi; print('ok')"` prints `ok`.

### 3. Run the tests. They should FAIL.
```
pytest -q
```
**Expected right now: about 32 failed, 2 skipped.** That is correct. Failing tests are your to-do list. The tests run **offline** with a fake model, so they work with or without the server.

### 4. Open the tunnel to the model server
Open a **new terminal** and leave it open all day:
```
ssh -L 11434:localhost:11434 <user>@<ec2-host>
```
Check (in another terminal):
```
curl http://localhost:11434/api/tags
```
(Windows PowerShell: `curl.exe http://localhost:11434/api/tags`.) You should see a list of models in JSON. If not, see `docs/troubleshooting.md`.

### 5. Find your squad
| Squad | You build | Your instructions | You edit only | Your tests |
|---|---|---|---|---|
| **1 Ingestion** | Split documents into chunks and index them | `docs/squad-1-ingestion.md` | `src/hsi_rag/ingest.py` | `tests/test_ingest.py` |
| **2 Query** | Find chunks, ask the model, cite or refuse | `docs/squad-2-query.md` | `src/hsi_rag/query.py` | `tests/test_query.py` |
| **3 API and UI** | HTTP API with a token, and a chat page | `docs/squad-3-api-ui.md` | `src/hsi_rag/api.py`, `src/hsi_rag/ui.py` | `tests/test_api.py` |
| **4 Evals and Ops** | Test questions, scorer, load test | `docs/squad-4-evals-ops.md` | `evals/run.py`, `tests/questions.yaml`, `scripts/load_test.py` | `tests/test_evals.py` |

Read `docs/00-start-here.md` once (5 minutes), then your squad file.

## About the knowledge base (`kb/`)
All 14 documents are **synthetic training data**, not official HSI documents. Ten are short summaries based on public information from the HSI website. Four are longer, **invented** test documents (`returnship-handbook.md`, `candidate-onboarding-guide.md`, `employer-partnership-guide.md`, `data-privacy-and-consent.md`) with made-up details so that chunking and retrieval have something realistic to work on. None of them contain fees or refund terms, so questions about those are meant to be refused.

## Golden rules
1. **Edit only your own files** (table above). Everything else is shared plumbing or belongs to another squad.
2. **Never change a contract.** Names, arguments and return shapes are in `docs/contracts.md`. Other squads rely on them.
3. **Call the model only through `llm.embed(...)` and `llm.chat(...)`**, written exactly like that. Never `from hsi_rag.llm import embed`. The tests swap these functions for fakes.
4. **Your tests must be green before you merge.**
5. **Stuck for 10 minutes? Ask.** A helper, another squad or the troubleshooting page. Do not struggle alone.

## Everyday commands
| What | Command |
|---|---|
| Run all tests | `pytest -q` |
| Run one squad's tests | `pytest tests/test_ingest.py -q` |
| Index the knowledge base for real | `python -m hsi_rag.ingest kb` |
| Quick-load the KB (until Squad 1 is done) | `python scripts/seed_kb.py` |
| Ask a question from Python | `python -c "from hsi_rag import query; print(query.answer('Who can join a returnship?'))"` |
| Start the API | `uvicorn hsi_rag.api:app --port 8000` |
| Start the chat UI | `streamlit run src/hsi_rag/ui.py` |
| Run the evals for real | `python -m evals.run` |
| Real-model integration tests | `RUN_INTEGRATION=1 pytest -m integration -q` (PowerShell: `$env:RUN_INTEGRATION="1"; pytest -m integration -q`) |

## Folder map
```
kb/                 the knowledge base (synthetic HSI documents)
src/hsi_rag/        config.py llm.py store.py   shared, do not edit
                    ingest.py                   Squad 1
                    query.py                    Squad 2
                    api.py ui.py                Squad 3
evals/run.py        Squad 4
scripts/            seed_kb.py (helper), load_test.py (Squad 4)
tests/              tests for every squad (do not edit, except questions.yaml)
docs/               instructions: start-here, one per squad, integration, troubleshooting
```

## Working with git
```
git checkout -b squad-1-ingestion        # use your squad's name
# ...work, run your tests...
git add -A && git commit -m "Squad 1: implement chunk and ingest"
git push -u origin squad-1-ingestion
```
At the **integration checkpoint** the squads merge in this order: 1, 2, 3, 4. Because each squad edits different files, there should be no conflicts. See `docs/integration.md`.
