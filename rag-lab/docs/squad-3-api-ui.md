# Squad 3: API and UI

## Your goal
Put the assistant behind a secure HTTP API, then build a simple chat page on top of it.

## You edit only
`src/hsi_rag/api.py` and `src/hsi_rag/ui.py`

## Your tests
`tests/test_api.py` (7 tests, all red at the start). They replace the answer function with a fake, so you do **not** wait for Squad 2.

## What you must deliver
| Request | Response |
|---|---|
| `GET /health` | `200 {"status": "ok"}` |
| `POST /ask` `{"question": "..."}` + `Authorization: Bearer <token>` | `200` + the answer dictionary |
| no or wrong token | `401` |
| missing or empty `question` | `422` |
| model server down (`ConnectionError`) | `503` |

Details are in `docs/contracts.md` (Contract 3).

## Step by step

### Step 1: See the tests fail
```
pytest tests/test_api.py -q
```
Check: 7 failed.

### Step 2: The API (`api.py`)
Idea (code-along 10):
1. `app = FastAPI(...)` already exists. Add a pydantic model `Ask` with `question: str = Field(min_length=1)` (import `Field` from pydantic). FastAPI then returns `422` for you.
2. `@app.get("/health")` returns `{"status": "ok"}`.
3. `@app.post("/ask")` takes `body: Ask` and `authorization: str = Header("")`.
4. Check the token: read `os.environ.get("HSI_API_TOKEN", "")` **inside the handler** (not at the top of the file). If it is empty or `authorization != f"Bearer {token}"`, `raise HTTPException(status_code=401)`.
5. Call `query.answer(body.question)` exactly like that (not `from .query import answer`), and return the result.
6. Wrap the call in `try/except (ConnectionError, OSError)` and raise `HTTPException(status_code=503, ...)`.

Check:
```
pytest tests/test_api.py -q
```
Expected: 7 passed.

### Step 3: Run it for real
Terminal 1 (tunnel open, knowledge base loaded with `python scripts/seed_kb.py` or Squad 1's ingest):
```
export HSI_API_TOKEN=dev-token             # PowerShell: $env:HSI_API_TOKEN="dev-token"
uvicorn hsi_rag.api:app --port 8000
```
Terminal 2:
```
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"Who can join a returnship?\"}"
curl -X POST http://127.0.0.1:8000/ask -H "Authorization: Bearer dev-token" -H "Content-Type: application/json" -d "{\"question\": \"Who can join a returnship?\"}"
```
(PowerShell: use `curl.exe`.) Expected: health is `ok`; the second call is `401`; the third returns an answer with sources.

### Step 4: The chat page (`ui.py`)
Using Streamlit (the imports are already there):
1. `st.title("HSI Assistant")`.
2. `question = st.text_input("Ask a question")` and `st.button("Ask")`.
3. On click: `requests.post(f"{API_URL}/ask", json={"question": question}, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=120)`.
4. Show `data["answer"]` with `st.write`, and under it the sources with `st.caption`.
5. Handle errors with `st.error(...)`: `401` (check the token), `503` (model server unavailable), and a network failure. Never show a stack trace.

Run:
```
streamlit run src/hsi_rag/ui.py
```
Check: ask a question in the browser; you see an answer and sources. Stop the tunnel and ask again: you see a friendly error.

## Done when
- [ ] `pytest tests/test_api.py -q` shows 7 passed
- [ ] the three curl commands behave as described
- [ ] the chat page shows an answer and sources, and a clear error when things fail
- [ ] your work is committed and pushed

## Hints
- `Header("")` gives an empty string when the header is missing, so one comparison covers "missing" and "wrong".
- If the test says `401` is expected but you get `422`, your validation runs before auth. That is fine only if the body is invalid.
- Do not put the real token in the code. It comes from the environment.

## Stretch goals (only when everything is green)
1. Show a chat history in the UI (`st.session_state`).
2. Add request logging: question length, latency and status, but **not** the question text (privacy).
3. Return a request id header on every response.

## If you are blocked
- Squad 2 not ready? The tests already fake `query.answer`. For manual runs, temporarily return a fixed dictionary from your own code path; remove it before merging.
- Port 8000 busy: `uvicorn ... --port 8001` and set `API_URL=http://127.0.0.1:8001`.
