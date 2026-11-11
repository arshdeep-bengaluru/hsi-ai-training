"""Shared settings. Do not change the REFUSAL text or COLLECTION name: tests and
every squad depend on them. Read values from this module at call time
(config.CHROMA_PATH), never copy them into your own module-level variables."""
import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "chroma_db")

COLLECTION = "hsi_kb"
TOP_K = 4
REFUSAL = "I don't have that information. Please ask the HSI team."
