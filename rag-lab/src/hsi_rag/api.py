"""SQUAD 3 - API. You own this file (and ui.py).

Read docs/squad-3-api-ui.md first. Your tests: tests/test_api.py

Run locally:   uvicorn hsi_rag.api:app --port 8000
"""
from fastapi import FastAPI

from . import query  # noqa: F401  (call it as query.answer(...), see the docs)

app = FastAPI(title="HSI assistant")

# Squad 3: add
#   GET  /health  -> {"status": "ok"}
#   POST /ask     -> body {"question": str (not empty)}, returns query.answer(question)
# with bearer-token auth and the error handling described in docs/squad-3-api-ui.md
