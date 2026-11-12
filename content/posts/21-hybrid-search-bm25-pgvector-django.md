---
title: Hybrid Search with BM25 and pgvector in Django
category: Search
status: published
---
## Why one signal is not enough
Keyword search with BM25 finds exact terms and rare phrases. Vector search with pgvector finds meaning even when the words differ. Used alone, each misses cases the other catches. A hybrid query runs both, normalizes their scores, and combines them so a result can rank high from either strong keyword match or strong semantic match.

In a blog or documentation corpus this matters. A user may search for the exact function name or for a description of the problem it solves. Returning only one style of result leaves useful pages lower than they should be.

## How the scores are combined
Run the BM25 (or Postgres full-text) query and the vector distance query separately. Each returns a ranked list with a raw score. Convert both scores to a common 0–1 range, then compute a weighted sum. A typical starting weight is 0.5 for each; adjust after looking at real queries.

Postgres can do the combination in one SQL statement with a CTE or a subquery, or you can fetch modest candidate sets (a few hundred rows) from each method and merge them in Python. The SQL approach keeps data transfer small. The Python approach makes weight tuning and debugging easier while the feature is new.

```python
from django.contrib.postgres.search import SearchQuery, SearchRank
from pgvector.django import CosineDistance

def hybrid_search(query_text, query_vector, limit=10):
    keyword = (
        Post.objects
        .annotate(rank=SearchRank("search_vector", SearchQuery(query_text)))
        .filter(rank__gt=0.1)
        .order_by("-rank")[:100]
    )
    vector = (
        Post.objects
        .annotate(distance=CosineDistance("embedding", query_vector))
        .order_by("distance")[:100]
    )
    # normalize and merge in Python, then return top `limit`
    return merge_and_rerank(keyword, vector, limit)
```

## Index and filter placement
The full-text side needs a GIN index on the tsvector column. The vector side needs an HNSW (or IVFFlat) index. Both benefit from the same selective filters applied first: status = published, category, date range. Filtering before the ranking step keeps the candidate sets small and lets each index do less work.

Store the tsvector and the embedding on the same row (or on a closely related sentence row) so a single query can see both. If you use sentence-level vectors, aggregate the best sentence score back to the post before merging with the post-level BM25 score.

## Tuning and evaluation
Log a sample of real queries and the top results from keyword-only, vector-only, and hybrid. Note which relevant pages each method missed. Increase the vector weight if users paraphrase; increase the keyword weight if they paste error messages or function names. Re-check after any change to chunking or embedding model, because those alter the vector scores.

A simple offline test set of twenty or thirty questions with known good posts is enough to spot regressions. You do not need a full relevance-judgment platform while the corpus is still growing.

## What good looks like
A query that contains a rare exact term ranks the page that uses that term near the top even if the surrounding language is different. A query that describes a concept without using the page’s keywords still surfaces the right page. The combined latency stays comparable to the slower of the two individual searches. If hybrid results are consistently worse than the better of the two single methods, the normalization or the weights need adjustment before more features are added.