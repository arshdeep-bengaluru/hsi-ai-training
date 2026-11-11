# Squad 1: Ingestion

## Your goal
Turn the documents in `kb/` into searchable chunks stored in Chroma, safely and repeatably.

## You edit only
`src/hsi_rag/ingest.py`

## Your tests
`tests/test_ingest.py` (8 tests, all red at the start)

## What you must deliver
```python
def chunk(text: str, size: int = 500, overlap: int = 60) -> list[str]
def ingest(path: str) -> int
```
Details are in `docs/contracts.md` (Contract 1). In short: chunk by **words**, and store each chunk with id `"<file>-<index>"` and metadata `source`, `chunk_id`, `title`.

## Step by step

### Step 1: See the tests fail
```
pytest tests/test_ingest.py -q
```
Check: 8 failed. Read the test file; it tells you exactly what is expected.

### Step 2: Implement `chunk()`
Open `src/hsi_rag/ingest.py`. Idea (also code-along 5 in the slides):
1. `words = text.split()`; if there are no words, return `[]`.
2. The window moves forward by `step = size - overlap` words each time.
3. Each chunk is `" ".join(words[i : i + size])`.
4. Stop once a chunk reaches the end of the text (`i + size >= len(words)`).

Check:
```
pytest tests/test_ingest.py -k chunk -q
```
Expected: 4 passed.

Common mistake: forgetting to stop at the end, which creates a tiny last chunk that only repeats the overlap.

### Step 3: Implement `ingest()`
Idea (code-along 6):
1. Get the collection: `col = store.get_collection()`.
2. For each file in `sorted(Path(path).glob("*.md"))`: read it, `chunk(...)` it, skip if no chunks.
3. Make ids: `f"{f.name}-{i}"` for each chunk index `i`.
4. `col.upsert(ids=..., documents=..., embeddings=llm.embed(pieces), metadatas=[...])`.
5. Add up and return the total number of chunks.

Use `upsert` (not `add`) with these stable ids. That is what makes running twice safe.
Write `llm.embed(...)`, never `from hsi_rag.llm import embed`.

Check:
```
pytest tests/test_ingest.py -q
```
Expected: 8 passed.

### Step 4: Run it for real
Make sure your tunnel is open (see `docs/00-start-here.md`), then:
```
python -m hsi_rag.ingest kb
```
Expected: a line like `Indexed 10 chunks into 'hsi_kb' at chroma_db`.
Run it **again**: the number must be the same, and there must be no growth. Check in Python:
```
python -c "from hsi_rag import store; print(store.get_collection().count())"
```

### Step 5: Tell the others
Post in your channel: "Squad 1 green." Squads 2 to 4 can now use your real index instead of `scripts/seed_kb.py`.

## Done when
- [ ] `pytest tests/test_ingest.py -q` shows 8 passed
- [ ] `python -m hsi_rag.ingest kb` works against the real model
- [ ] running it twice does not change the chunk count
- [ ] every chunk has `source`, `chunk_id` and `title`
- [ ] your work is committed and pushed

## Hints
- The knowledge base documents are short, so with `size=500` each file becomes **one** chunk. That is fine. To see chunking matter, try `size=80, overlap=10` and compare answers later with Squad 4's evals.
- `Path(path).glob("*.md")` returns files in no fixed order: use `sorted(...)` so ids are stable.
- `chunk_id` in the metadata must be the same string as the id.

## Stretch goals (only when everything is green)
1. Split on headings (`## `) first, then by size, so each chunk is one topic.
2. Delete stale chunks: if a file gets shorter, its old high-numbered chunks are still in the index. Remove them.
3. Add a `--size` option to the command line and compare results with Squad 4.

## If you are blocked
- Model connection errors: `docs/troubleshooting.md`.
- Not sure about a return shape: `docs/contracts.md`.
- Another squad needs your index early: tell them to run `python scripts/seed_kb.py` until you are done.
