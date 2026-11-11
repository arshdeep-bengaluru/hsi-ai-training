"""The ONLY place that talks to Ollama. Shared plumbing: do not edit.

Everyone must call these as `llm.embed(...)` and `llm.chat(...)` (module
attribute access). Never write `from hsi_rag.llm import embed`: the tests replace
these two functions with fakes so they run without a model server.
"""
import ollama

from . import config


def _client() -> ollama.Client:
    return ollama.Client(host=config.OLLAMA_HOST)


def embed(texts: list[str]) -> list[list[float]]:
    """One embedding vector per input text."""
    response = _client().embed(model=config.EMBED_MODEL, input=texts)
    return response["embeddings"]


def chat(prompt: str, temperature: float = 0.0) -> str:
    """Send one user prompt to the LLM and return the reply text."""
    response = _client().chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature},
    )
    return response["message"]["content"]
