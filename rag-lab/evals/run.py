"""SQUAD 4 - EVALS. You own this file, tests/questions.yaml and scripts/load_test.py.

Read docs/squad-4-evals-ops.md first. Your tests: tests/test_evals.py
Run for real:  python -m evals.run
"""
import sys  # noqa: F401

import yaml  # noqa: F401

from hsi_rag import config  # noqa: F401


def run(path: str = "tests/questions.yaml", answer_fn=None) -> dict:
    """Run every question in the YAML file and score it.

    `answer_fn(question) -> {"answer": str, "sources": [...]}`; if None, use
    hsi_rag.query.answer. Return:

        {"results": [{"id", "type", "correct", "cited", "safe", "passed"}, ...],
         "passed": <int>, "failed": <int>}

    Scoring rules are in docs/squad-4-evals-ops.md.
    """
    raise NotImplementedError("Squad 4: implement run()")


def main(argv: list[str] | None = None) -> int:
    """Print one PASS/FAIL line per question plus a summary. Return 0 if all passed, else 1."""
    raise NotImplementedError("Squad 4: implement main()")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
