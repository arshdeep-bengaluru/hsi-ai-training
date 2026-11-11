# Take-home task: hybrid search for the HSI assistant

**Do this offline, after the workshop.** Estimated effort: 2 to 4 hours.

## Why
Vector search finds meaning but can miss exact terms: program names, fees, dates, acronyms (for example "UiPath Career Day" or "EPF"). Keyword search (BM25) is strong on exact terms but blind to paraphrase. Combining them (hybrid search) is the usual first upgrade over naive RAG.

## Goal
Improve retrieval for exact-term questions without breaking the contract:

- `answer(question) -> {"answer": str, "sources": [{"source", "chunk_id"}]}` is unchanged.
- `REFUSAL` behaviour is unchanged: trap and privacy questions still return exactly `REFUSAL` with `sources == []`.

## Steps
1. **Add keyword search.** Build a BM25 index over the same chunks stored in `hsi_kb` (for example with `rank_bm25`). Rebuild it whenever `ingest()` runs.
2. **Rank both ways.** For a question, get a ranked list of chunk ids from the vector search and another from BM25.
3. **Fuse.** Combine the two lists with reciprocal rank fusion (RRF) and keep the top k.
4. **Wire it in.** Make `retrieve()` return the fused hits; leave `answer()` and the API alone.
5. **Measure.** Add 5 to 8 exact-term questions to `tests/questions.yaml` (fees, program names, dates). Run the evals before and after. Record the numbers.
6. **Write a one-page note:** what you changed, the before/after eval results, and anything that got worse.

## Starter snippet
```python
from rank_bm25 import BM25Okapi

bm25 = BM25Okapi([t.lower().split() for t in texts])
kw = bm25.get_scores(q.lower().split())
# turn kw into a ranked list of chunk ids

def rrf(rank_lists, k=60):
    score = {}
    for ranks in rank_lists:
        for pos, cid in enumerate(ranks):
            score[cid] = score.get(cid, 0) + 1 / (k + pos + 1)
    return sorted(score, key=score.get, reverse=True)
```

## Done when
- Exact-term eval questions pass more often than before.
- All previous eval questions still pass (no regressions).
- The one-page note is written.

## Optional extras
- Add a reranker over the fused top results.
- Add metadata filters (for example restrict to one program's documents).
- Tune k and the RRF constant using the evals, not by guessing.
