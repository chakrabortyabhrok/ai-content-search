from rag.chunking import split_sentences, split_post


def test_abbreviation_stays_together():
    out = split_sentences("See e.g. this works.")
    assert out == ["See e.g. this works."]


def test_short_fragment_is_glued():
    out = split_sentences("Hello world. Yes.")
    assert out == ["Hello world. Yes."]


def test_heading_is_not_a_chunk():
    post = "## Install\n\nRun the command."
    chunks = split_post(post)
    assert len(chunks) == 1
    assert chunks[0]["section"] == "Install"
    assert chunks[0]["is_code"] is False


def test_code_block_stays_whole():
    post = "Before.\n\n```python\nprint('hi.')\n```\n\nAfter."
    chunks = split_post(post)
    code = [c for c in chunks if c["is_code"]]
    assert len(code) == 1
    assert "print" in code[0]["text"]
