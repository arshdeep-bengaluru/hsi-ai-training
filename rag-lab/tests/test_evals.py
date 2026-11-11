"""Squad 4 tests. Do not edit.

These check (a) your question file and (b) your scorer, using fake answer functions.
"""
from pathlib import Path

import yaml

from evals import run as evals_run
from hsi_rag import config

QPATH = Path(__file__).parent / "questions.yaml"
KB = Path(__file__).resolve().parent.parent / "kb"


def load():
    return yaml.safe_load(QPATH.read_text(encoding="utf-8"))


def perfect(question):
    """A fake assistant that answers every question correctly."""
    q = next(x for x in load() if x["question"] == question)
    if q["type"] == "answerable":
        text = " ".join(q.get("expect_contains", [])) or "ok"
        return {"answer": text, "sources": [{"source": q["expect_source"], "chunk_id": q["expect_source"] + "-0"}]}
    return {"answer": config.REFUSAL, "sources": []}


def test_question_file_has_enough_good_questions():
    qs = load()
    assert len(qs) >= 10, "write at least 10 questions"
    ids = [q["id"] for q in qs]
    assert len(ids) == len(set(ids)), "ids must be unique"
    types = [q["type"] for q in qs]
    assert set(types) <= {"answerable", "trap", "privacy"}
    assert types.count("trap") >= 3, "need at least 3 trap questions"
    assert types.count("privacy") >= 1, "need at least 1 privacy question"
    for q in qs:
        assert q["question"].strip()
        if q["type"] == "answerable":
            assert (KB / q["expect_source"]).exists(), f"{q['id']}: expect_source not in kb/"


def test_results_have_the_required_fields():
    summary = evals_run.run(str(QPATH), answer_fn=perfect)
    for r in summary["results"]:
        assert {"id", "type", "correct", "cited", "safe", "passed"} <= set(r)


def test_perfect_assistant_passes_everything():
    summary = evals_run.run(str(QPATH), answer_fn=perfect)
    assert summary["failed"] == 0
    assert summary["passed"] == len(load())


def test_hallucinated_trap_answers_fail():
    def bad(question):
        return {"answer": "The fee is 5000 rupees.", "sources": []}

    summary = evals_run.run(str(QPATH), answer_fn=bad)
    traps = [r for r in summary["results"] if r["type"] == "trap"]
    assert traps and all(not r["passed"] for r in traps)


def test_missing_citation_fails_answerable_questions():
    def uncited(question):
        result = perfect(question)
        result["sources"] = []
        return result

    summary = evals_run.run(str(QPATH), answer_fn=uncited)
    answerable = [r for r in summary["results"] if r["type"] == "answerable"]
    assert answerable and all(not r["passed"] and not r["cited"] for r in answerable)


def test_wrong_content_is_not_correct():
    def wrong(question):
        result = perfect(question)
        if result["sources"]:
            result["answer"] = "zzz"
        return result

    summary = evals_run.run(str(QPATH), answer_fn=wrong)
    with_expected_text = [
        r for r in summary["results"]
        if r["type"] == "answerable" and any(q.get("expect_contains") for q in load() if q["id"] == r["id"])
    ]
    assert with_expected_text, "add expect_contains to at least one answerable question"
    assert all(not r["correct"] for r in with_expected_text)
