# Troubleshooting

## Setup

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: hsi_rag` or `evals` | Run commands from the `rag-lab/` folder, with the virtual environment active. `pytest.ini` sets the import paths. |
| `pytest: command not found` | Activate the environment (`source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`), then `pip install -r requirements.txt`. |
| PowerShell blocks `Activate.ps1` | Run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `.venv\Scripts\activate.bat` in cmd. |
| `pip install` fails on `chromadb` | Make sure Python is 3.10 or newer: `python --version`. |

## The tunnel and the model

| Problem | Fix |
|---|---|
| `ConnectionError` or `Connection refused` on port 11434 | The SSH tunnel is not running. Start it: `ssh -L 11434:localhost:11434 <user>@<ec2-host>` and keep that terminal open. |
| `ssh: Permission denied` | Wrong key or user. Ask a helper; do not try other people's keys. |
| `WARNING: UNPROTECTED PRIVATE KEY FILE` (Windows) | Only you may read the key file. In PowerShell: `icacls .\key.pem /inheritance:r` then `icacls .\key.pem /grant:r "$($env:USERNAME):(R)"`. Connect with `ssh -i .\key.pem -L 11434:localhost:11434 <user>@<ec2-host>`. |
| `ssh` hangs or times out | The network may block SSH (port 22). Try a phone hotspot and tell the facilitator. |
| `ssh` or `git` "is not recognized" (Windows) | Install Git for Windows / the OpenSSH Client (see the README checklist), then open a **new** terminal. |
| `bind: Address already in use` (11434) | You have a local Ollama running. Use another local port: `ssh -L 11500:localhost:11434 ...` and set `OLLAMA_HOST=http://localhost:11500`. |
| `model "..." not found` | The server does not have that model. Ask the facilitator which models are pulled; set `LLM_MODEL` / `EMBED_MODEL` to match. |
| Very slow first answer | The model is loading into memory on the server. Later calls are faster. |
| Everything is slow right now | 14 people share one server. Wait a moment, and avoid loops that call the model many times. |

## Tests

| Problem | Fix |
|---|---|
| Tests fail with `NotImplementedError` | That is the to-do list: implement the function named in the message. |
| A test passes for someone else but not you | Run only that test: `pytest tests/test_x.py::test_name -q -x` and read the first failure. |
| `integration` tests are skipped | By design. Set `RUN_INTEGRATION=1` (see the README) and open the tunnel. |
| Your code works for real but a test fails | You probably imported `embed` or `chat` by name. Use `llm.embed(...)` and `llm.chat(...)`. |
| API test cannot find the token | Read `os.environ.get("HSI_API_TOKEN")` inside the request handler, not at import time. |
| API test cannot replace the answer | Call `query.answer(...)` (module attribute), not `from .query import answer`. |

## Chroma (the vector store)

| Problem | Fix |
|---|---|
| Duplicate chunks after running ingest twice | Use `upsert` with stable ids (`<file>-<index>`), not `add`. |
| Strange results after changing the embedding model | Vectors from different models cannot be compared. Delete `chroma_db/` and ingest again. |
| `chroma_db` is corrupted | Stop all programs using it, delete the folder, ingest again. It is local and safe to recreate. |
| `Number of requested results is greater than number of elements` | Ask for `min(k, collection.count())` results. |

## API and UI

| Problem | Fix |
|---|---|
| `401` from curl | Add the header `Authorization: Bearer <token>` and make sure the server was started with the same `HSI_API_TOKEN`. |
| `422` | The body must be JSON with a non-empty `question`. |
| `503` | The model server is unreachable: check the tunnel. |
| Port 8000 busy | Use another port and set `API_URL`. |
| Streamlit shows nothing | Look at the terminal where you ran `streamlit run`; errors appear there. |

## Still stuck?
Tell a helper: which step you are on, the exact command, and the full error message (copy it, do not retype).
