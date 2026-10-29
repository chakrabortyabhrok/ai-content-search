from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from blog.models import Post, Category, Author
from rag.models import Sentence
from rag.chunking import split_sentences, split_post


class ChunkingLogicTests(TestCase):
    """Unit tests for text splitting and chunking utilities."""

    def test_split_sentences_abbreviations(self):
        """Ensure abbreviations like 'e.g.' or 'Dr.' do not fracture sentences prematurely."""
        text = "Dr. Smith went to the market, e.g., to buy fruits. He bought good red apples."
        sentences = split_sentences(text)
        
        # "Dr." should not split the sentence; should result in 2 clean sentences
        self.assertEqual(len(sentences), 2)
        self.assertIn("Dr. Smith", sentences[0])
        self.assertIn("He bought good red apples.", sentences[1])

    def test_split_sentences_min_words_merge(self):
        """Ensure very short fragments (< 4 words) are merged with the previous sentence."""
        text = "Django ORM is powerful. Yes."
        sentences = split_sentences(text)
        
        # "Yes." has 1 word (< 4), so it merges back into the preceding sentence
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0], "Django ORM is powerful. Yes.")

    def test_split_post_with_headings_and_code(self):
        """Test split_post correctly identifies headings, code blocks, and sentence structures."""
        content = """# Introduction
        Django is a Python web framework.
        ```python
        def hello():
        print('Hello World')


        # from rag.chunking import split_sentences, split_post

        # def test_abbreviation_stays_together():
        #     out = split_sentences("See e.g. this works.")
        #     assert out == ["See e.g. this works."]

        # def test_short_fragment_is_glued():
        #     out = split_sentences("Hello world. Yes.")
        #     assert out == ["Hello world. Yes."]

        # def test_heading_is_not_a_chunk():
        #     post = "## Install\n\nRun the command."
        #     chunks = split_post(post)
        #     assert len(chunks) == 1
        #     assert chunks[0]["section"] == "Install"
        #     assert chunks[0]["is_code"] is False

        # def test_code_block_stays_whole():
        #     post = "Before.\n\n```python\nprint('hi.')\n```\n\nAfter."
        #     chunks = split_post(post)
        #     code = [c for c in chunks if c["is_code"]]
        #     assert len(code) == 1
        #     assert "print" in code[0]["text"]

        """