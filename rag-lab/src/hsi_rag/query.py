"""SQUAD 2 - QUERY. You own this file.

Read docs/squad-2-query.md first. Your tests: tests/test_query.py
"""
from . import config, llm, store  # noqa: F401  (use llm.embed, llm.chat, store.get_collection)

REFUSAL = config.REFUSAL

# Write the grounded prompt template here. It must contain the placeholders
# {refusal}, {context} and {question}. See slides 25 and code-along 7.
PROMPT = ""


def retrieve(question: str, k: int | None = None) -> list[dict]:
    """Return the k nearest chunks (default config.TOP_K) from collection "hsi_kb".

    Each hit is a dict with keys: "text", "source", "chunk_id", "title", "dist".
    Return [] if the collection is empty. See code-along 8.
    """
    raise NotImplementedError("Squad 2: implement retrieve()")


def answer(question: str) -> dict:
    """Answer from the knowledge base. Returns exactly:

        {"answer": str, "sources": [{"source": str, "chunk_id": str}, ...]}

    If the model says it does not know (its reply, stripped, equals REFUSAL), return
    {"answer": REFUSAL, "sources": []}. See code-along 9.
    """
    raise NotImplementedError("Squad 2: implement answer()")
