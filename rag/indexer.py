"""
The single door: the ONLY code in this project that writes Sentence rows.
chunk -> embed -> store, for one post.
"""

from django.db import transaction

from blog.models import Post
from rag.chunking import split_post
from rag.embeddings import embed_post_chunks
from rag.models import Sentence


def index_post(post: Post) -> int:
    """
    (Re)index one post from scratch. Returns the number of sentences stored.
    Safe to call repeatedly: each run wipes this post's old sentences first.
    """
    # 1. Chunk — pure function, instant, no API.
    chunks = split_post(post.content)

    # 2. Embed — slow, network calls. Deliberately OUTSIDE the transaction:
    #    never hold database locks open while waiting on an API.
    vectors = embed_post_chunks(chunks, post.title)

    # Seatbelt: zip() silently stops at the shorter list. Without this
    # check, a mismatch would store misaligned rows and tell no one.
    if len(vectors) != len(chunks):
        raise RuntimeError(
            f"Embedding mismatch for '{post.title}': "
            f"{len(chunks)} chunks but {len(vectors)} vectors."
        )

    # 3. Store — fast, all-or-nothing. A reader asking a question mid-reindex
    #    sees the complete old index or the complete new one. Never half.
    with transaction.atomic():
        Sentence.objects.filter(post=post).delete()
        Sentence.objects.bulk_create(
            [
                Sentence(
                    post=post,
                    para_index=c["para_index"],
                    sent_index=c["sent_index"],
                    text=c["text"],  # clean sentence — no [Article...] prefix
                    section=c["section"],
                    is_code=c["is_code"],
                    embedding=v,
                )
                for c, v in zip(chunks, vectors)
            ],
            batch_size=500,
        )

    return len(chunks)
