"""
Question in -> most relevant Sentence rows out.
The READ side of the pipeline (indexer.py is the WRITE side).
    question --embed_query--> vector --pgvector search--> top-k sentences
"""

from pgvector.django import CosineDistance

from rag.embeddings import embed_query
from rag.models import Sentence

DEFAULT_K = 5  # how many sentences to return when the caller doesn't say


def retrieve(question: str, k: int = DEFAULT_K) -> list[dict]:
    """
    Find the k sentences whose meaning is closest to `question`.

    Returns a list of dicts, closest first. Each dict should carry enough
    to (a) show the text and (b) cite where it came from, e.g.:
        {text, distance, post_id, post_title, post_slug,
        section, para_index, sent_index, is_code}
    """

    # TODO 1: Guard against empty/whitespace-only questions.
    #         What should you return so callers don't crash?

    # TODO 2: Embed the question.
    #         Hint: embeddings.py already has the function — which side of
    #         the embedding space is a question on, "query" or "document"?

    # TODO 3: Start a queryset of Sentence rows, keeping only those whose
    #         post is published (and that actually have an embedding).
    #         Hint: Django lets you filter across a ForeignKey with `__`.
    #         Look at Post.status in blog/models.py for the exact value.

    # TODO 4: Annotate each row with its cosine distance to the question.
    #         Hint: look up `.annotate()` and pgvector's CosineDistance(field, vector).
    #         Smaller distance = more similar (0 = identical direction).

    # TODO 5: Order by that distance and slice the top k.
    #         Hint: querysets are lazy — slicing becomes SQL LIMIT.
    #         Also: you'll read post.title for every row. How do you avoid
    #         one extra query per row? (search: select_related)

    # TODO 6: Turn each row into a plain dict with _to_dict() and return the list.

    raise NotImplementedError


def _to_dict(sentence: Sentence) -> dict:
    """
    One Sentence row (with its annotated distance) -> one plain dict.

    Why a dict and not the model object? Callers (views, the LLM prompt,
    citations.py) shouldn't need to know about Django models.
    """

    # TODO 7: Build and return the dict described in retrieve()'s docstring.
    #         The annotated value lives on the object under whatever name
    #         you gave it in .annotate(...).

    raise NotImplementedError
