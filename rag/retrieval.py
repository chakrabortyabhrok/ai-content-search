"""
Question in -> most relevant Sentence rows out.
The READ side of the pipeline (indexer.py is the WRITE side).
    question --embed_query--> vector --pgvector search--> top-k sentences
"""

from django.db import connection, transaction
from pgvector.django import CosineDistance
from rag.embeddings import embed_query
from rag.models import Sentence

DEFAULT_K = 5  # how many sentences to return when the caller doesn't say

# HNSW is APPROXIMATE. With pgvector's default (ef_search=40) the staging-password
# question returned "Rate-limit login and chat." (distance 0.768) and missed the
# real answer (0.675) - even after a REINDEX. 200 was the first value that found it;
# 400 adds margin. At ~2k rows this is still a few ms. Revisit when rows reach 100k+.
HNSW_EF_SEARCH = 400


def retrieve(question: str, k: int = DEFAULT_K) -> list[dict]:
    """
    Find the k sentences whose meaning is 'closest to question'.

    Returns a list of dicts, closest first. Each dict carries the hit, its
    neighbours in the same paragraph, and enough to cite where it came from:
        {hit, before, after, section, post_title, post_slug,
         distance, para_index, sent_index}
    """

    if not question or not question.strip():
        return []

    query_vector = embed_query(question.strip())

    # SET LOCAL only lasts until the transaction ends, so it can't leak into
    # other queries. list() forces the query to run INSIDE the transaction.
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL hnsw.ef_search = {int(HNSW_EF_SEARCH)}")
        rows = list(
            Sentence.objects.filter(post__status="published", embedding__isnull=False)
            .annotate(distance=CosineDistance("embedding", query_vector))
            .order_by("distance")
            .select_related("post")[:k]
        )

    return [_to_dict(row) for row in rows]


def _neighbour_text(sentence: Sentence, offset: int) -> str | None:
    """
    Text of the sentence `offset` places away in the SAME paragraph, or None.
    offset = -1 -> the sentence before, offset = +1 -> the sentence after.
    """

    neighbour = Sentence.objects.filter(
        post_id=sentence.post_id,
        para_index=sentence.para_index,
        sent_index=sentence.sent_index + offset,
    ).first()

    return neighbour.text if neighbour else None


def _to_dict(sentence: Sentence) -> dict:
    """
    One Sentence row (with its annotated distance) -> one plain dict.

    Why a dict and not the model object? Callers (views, the LLM prompt,
    citations.py) shouldn't need to know about Django models.
    """

    return {
        "hit": sentence.text,
        "before": _neighbour_text(sentence, -1),
        "after": _neighbour_text(sentence, +1),
        "section": sentence.section,
        "post_title": sentence.post.title,
        "post_slug": sentence.post.slug,
        "distance": sentence.distance,  # the hit's score only
        "para_index": sentence.para_index,
        "sent_index": sentence.sent_index,
    }
