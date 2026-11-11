# Squad 2: Query

## Your goal
Given a question, find the best chunks, ask the model to answer **only from them**, cite the sources, and refuse when the answer is not there.

## You edit only
`src/hsi_rag/query.py`

## Your tests
`tests/test_query.py` (10 tests, all red at the start). They load the knowledge base for you, so you do **not** wait for Squad 1.

## What you must deliver
```python
PROMPT = "..."                                   # the grounded prompt template
def retrieve(question: str, k: int | None = None) -> list[dict]
def answer(question: str) -> dict
```
Details are in `docs/contracts.md` (Contract 2).

## Step by step

### Step 1: See the tests fail
```
pytest tests/test_query.py -q
```
Check: 10 failed.

### Step 2: Write `PROMPT`
It is a string with three placeholders: `{refusal}`, `{context}`, `{question}`. Order: rules, refusal instruction, context, question last (slide 25, code-along 7):
```
Answer ONLY from the context below.
Cite sources like [faq.md-0].
If the answer is not in the context, reply exactly:
{refusal}

CONTEXT:
{context}

QUESTION: {question}
```
Keep it short. Small models follow short prompts better.

### Step 3: Implement `retrieve()`
Idea (code-along 8):
1. `col = store.get_collection()`. If `col.count() == 0`, return `[]`.
2. `res = col.query(query_embeddings=llm.embed([question]), n_results=min(k, col.count()))`, with `k` defaulting to `config.TOP_K`.
3. Chroma returns lists of lists: use `res["documents"][0]`, `res["metadatas"][0]`, `res["distances"][0]`.
4. Return a list of dictionaries: `{"text": document, **metadata, "dist": distance}`.

Check:
```
pytest tests/test_query.py -k retrieve -q
```
Expected: 4 passed.

### Step 4: Implement `answer()`
Idea (code-along 9):
1. `hits = retrieve(question)`. If none, return `{"answer": REFUSAL, "sources": []}`.
2. Build the context: one line per hit, `f"[{h['chunk_id']}] {h['text']}"`, joined with blank lines.
3. `text = llm.chat(PROMPT.format(refusal=REFUSAL, context=context, question=question)).strip()`.
4. If `text == REFUSAL`, return `{"answer": REFUSAL, "sources": []}`.
5. Otherwise return `{"answer": text, "sources": [{"source": ..., "chunk_id": ...}, ...]}` built from the hits.

Always write `llm.chat(...)` this way, and use `config.REFUSAL` (available here as `REFUSAL`).

Check:
```
pytest tests/test_query.py -q
```
Expected: 10 passed.

### Step 5: Try it with the real model
Open the tunnel. Load the knowledge base (`python -m hsi_rag.ingest kb` if Squad 1 is done, otherwise `python scripts/seed_kb.py`). Then:
```
python -c "from hsi_rag import query; print(query.answer('Who can join a returnship?'))"
python -c "from hsi_rag import query; print(query.answer('What is the exact fee for the Java Full Stack Returnship?'))"
```
Expected: the first answers with sources; the second prints exactly the refusal sentence with `sources: []`. If the second invents a fee, improve the prompt (see hints).

## Done when
- [ ] `pytest tests/test_query.py -q` shows 10 passed
- [ ] a real question returns an answer with sources
- [ ] a question not in the documents returns exactly the refusal with no sources
- [ ] your work is committed and pushed

## Hints
- **Debug retrieval first.** If an answer is wrong, print `query.retrieve("...")`. Are the right chunks there? If not, no prompt will help.
- If the model does not refuse properly: put the refusal instruction right before the context, repeat it after the question, or lower the number of chunks.
- Temperature is already 0 in `llm.chat` by default. Keep it.
- Models sometimes add extra words around the refusal. The contract allows only exact equality after `.strip()`; make the prompt say "reply exactly".

## Stretch goals (only when everything is green)
1. Return only the sources the answer actually cites (look for `[chunk_id]` in the text) and fall back to all hits if none are cited.
2. Add a distance threshold: if the best hit is too far away, refuse **without** calling the model.
3. Hybrid search is the take-home task (see `../docs/take-home-hybrid-search.md` in the training repo).

## If you are blocked
- Squad 1 not ready? You do not need them: tests have their own data, and `python scripts/seed_kb.py` loads the real index.
- Model connection errors: `docs/troubleshooting.md`.
