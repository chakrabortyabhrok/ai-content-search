"""
The ONLY file in this project that talks to Voyage_API.
If ever switched embedding models, this file is the only job.
Chunk dicts -> Vectors
"""

import time
import voyageai

vo = voyageai.Client()  # reads VOYAGE_API_KEY from the environment

MODEL = "voyage-context-4"  # If change models - change this line
OUTPUT_DIMENSION = 1024  # must match VectorField(dimensions=1024) in models.py

MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2  # waits 2s, then 4s


def _with_context(chunk: dict, post_title: str) -> str:
    """
    Stamp the post title + section onto a chunk — for embedding only.

    Why: our chunker keeps headings OUT of the chunk stream (they live in
    the `section` field). Without this, the model never sees them.
    """
    context = f"Article: {post_title}"
    if chunk["section"]:
        context += f" | Section: {chunk['section']}"
    return f"[{context}]\n{chunk['text']}"


def embed_post_chunks(chunks: list[dict], post_title: str) -> list[list[float]]:
    """
    All chunks of ONE post -> their embeddings, same order. One API call.
    """
    if not chunks:
        return []

    # [[c1, c2, c3]] = ONE document, pre-split into chunks.

    inputs = [[_with_context(c, post_title) for c in chunks]]

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = vo.contextualized_embed(
                model=MODEL,
                inputs=inputs,
                input_type="document",
                output_dimension=OUTPUT_DIMENSION,
            )
            return result.results[0].embeddings
        except Exception:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_WAIT_SECONDS * (2 ** (attempt - 1)))


def embed_query(question: str) -> list[float]:
    """
    A user question -> one embedding.

    Same model, but input_type="query" — the model is trained with two
    sides to its embedding space.
    """
    result = vo.contextualized_embed(
        model=MODEL,
        inputs=[question],
        input_type="query",
        output_dimension=OUTPUT_DIMENSION,
    )
    return result.results[0].embeddings[0]
