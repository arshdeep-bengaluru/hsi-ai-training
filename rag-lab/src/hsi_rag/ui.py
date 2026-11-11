"""SQUAD 3 - CHAT UI (Streamlit). You own this file.

Run:  streamlit run src/hsi_rag/ui.py

Build a page with a title, a question box and an Ask button. On click, POST the question
to the API (env API_URL, default http://127.0.0.1:8000) with header
"Authorization: Bearer <HSI_API_TOKEN>", then show the answer and, under it, the sources.
Show a clear message (not a stack trace) if the API or the model is unavailable.
"""
import os

import requests  # noqa: F401
import streamlit as st  # noqa: F401

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
TOKEN = os.environ.get("HSI_API_TOKEN", "")

# Squad 3: build the page here.
