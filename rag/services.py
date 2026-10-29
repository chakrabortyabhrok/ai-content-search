from rag.models import Sentence
from rag.chunking import split_post


def save_sentences(post):
    """Rebuild stored sentences for one post. Safe to run twice."""
    if post.status != "published":
        post.sentences.all().delete()
        return 0

    pieces = split_post(post.content or "")

    post.sentences.all().delete()

    rows = [
        Sentence(
            post=post,
            para_index=piece["para_index"],
            sent_index=piece["sent_index"],
            text=piece["text"],
            section=piece.get("section", ""),
            is_code=piece.get("is_code", False),
        )
        for piece in pieces
    ]

    Sentence.objects.bulk_create(rows)
    return len(rows)