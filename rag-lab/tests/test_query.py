"""Squad 2 tests. Do not edit."""
from hsi_rag import config, query

QUESTION = "Who can join a returnship?"


def test_retrieve_returns_hits_with_required_keys(seeded):
    hits = query.retrieve(QUESTION)
    assert 1 <= len(hits) <= config.TOP_K
    for h in hits:
        assert {"text", "source", "chunk_id", "title", "dist"} <= set(h)


def test_retrieve_respects_k(seeded):
    assert len(query.retrieve(QUESTION, k=2)) == 2


def test_retrieve_finds_the_right_document(seeded):
    sources = {h["source"] for h in query.retrieve(QUESTION)}
    assert "returnship-faq.md" in sources


def test_retrieve_on_empty_collection_returns_nothing():
    assert query.retrieve(QUESTION) == []


def test_answer_returns_the_contract_shape(seeded, fake_chat):
    result = query.answer(QUESTION)
    assert set(result) == {"answer", "sources"}
    assert isinstance(result["answer"], str) and result["answer"]
    assert result["sources"]
    for s in result["sources"]:
        assert set(s) == {"source", "chunk_id"}


def test_answer_cites_the_expected_source(seeded, fake_chat):
    result = query.answer(QUESTION)
    assert "returnship-faq.md" in {s["source"] for s in result["sources"]}


def test_refusal_is_exact_and_has_no_sources(seeded, fake_chat):
    fake_chat.reply = config.REFUSAL
    assert query.answer("What is the exact fee for the Java program?") == {
        "answer": config.REFUSAL,
        "sources": [],
    }


def test_refusal_ignores_surrounding_whitespace(seeded, fake_chat):
    fake_chat.reply = "  " + config.REFUSAL + "\n"
    assert query.answer("anything")["sources"] == []


def test_empty_knowledge_base_refuses():
    assert query.answer(QUESTION) == {"answer": config.REFUSAL, "sources": []}


def test_prompt_is_grounded(seeded, fake_chat):
    query.answer(QUESTION)
    prompt = fake_chat.prompts[-1]
    assert config.REFUSAL in prompt
    assert QUESTION in prompt
    assert "returnship-faq.md-" in prompt  # a retrieved chunk id appears in the context
