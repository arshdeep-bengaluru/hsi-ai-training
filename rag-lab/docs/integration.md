# Integration checkpoint

When: after the squad build block. Goal: the four parts run together and the real evals pass.

## 1. Merge (in this order)
Squads edit different files, so there should be no conflicts. One person per squad, in order 1, 2, 3, 4:
```
git checkout main
git pull
git merge squad-1-ingestion     # then squad-2-query, squad-3-api-ui, squad-4-evals-ops
pytest -q                       # after each merge
```
Expected after all four: **all tests pass, 2 skipped** (the integration tests).

If a merge conflicts, it means a squad edited a file it does not own. Resolve by keeping the owner's version of that file.

## 2. Build the real index
Tunnel open:
```
python -m hsi_rag.ingest kb
```
Check: prints the number of chunks; running again prints the same number.

## 3. Run the real-model integration tests
macOS/Linux: `RUN_INTEGRATION=1 pytest -m integration -q`
PowerShell: `$env:RUN_INTEGRATION="1"; pytest -m integration -q`

Expected: `test_ollama_is_reachable` and `test_real_model_passes_the_whole_eval` pass. If the second fails it lists the failing question ids.

## 4. Run the evals and read them
```
python -m evals.run
```
For each FAIL, decide which kind it is and send it to the owner:

| Symptom | Likely cause | Owner |
|---|---|---|
| Right document not in `retrieve()` output | chunking, `k`, or the embedding | Squad 1 / Squad 2 |
| Right chunks retrieved, answer wrong or invented | prompt, too much context, model | Squad 2 |
| Trap question answered instead of refused | prompt not strict; add the refusal rule near the question | Squad 2 |
| Answer right but `cited` false | sources not returned, or wrong file name | Squad 2 |
| Document missing in the knowledge base | add or fix a file in `kb/` | all |

Fix the **worst** failures first, then re-run. Always check retrieval before blaming the model.

## 5. Check the API and UI end to end
```
export HSI_API_TOKEN=dev-token       # PowerShell: $env:HSI_API_TOKEN="dev-token"
uvicorn hsi_rag.api:app --port 8000
streamlit run src/hsi_rag/ui.py
```
Ask a real question and a trap question in the browser.

## 6. Hand over to deployment
When the real evals pass, tell the facilitator. Deployment (service, auth, load test) is the next block.
