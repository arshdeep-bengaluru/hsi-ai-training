"""SQUAD 4 - LOAD TEST. You own this file.

Goal: simulate 14 people asking questions at the same time (plus, optionally, a re-ingest
running in parallel) and report latency. See docs/squad-4-evals-ops.md, step 6.

Suggested usage:  python scripts/load_test.py --users 14 --rounds 3

Print: number of requests, errors, p50 and p95 latency in seconds.
Hint: concurrent.futures.ThreadPoolExecutor + requests.post to the /ask endpoint with the
bearer token; collect time.perf_counter() differences; use statistics.quantiles for p95.
"""

raise SystemExit("Squad 4: implement scripts/load_test.py")
