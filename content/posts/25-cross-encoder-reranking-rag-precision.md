---
title: Cross-Encoder Reranking for RAG Precision
category: RAG
status: published
---
## Retrieval finds candidates, reranking orders them
A fast vector or hybrid search returns a few dozen candidate chunks. Those candidates are usually relevant, but their order is only approximate. A cross-encoder looks at the query and each candidate together and produces a much finer relevance score. Reordering the top candidates with that score lifts the best passages to the front before they are sent to the language model.

The extra cost is acceptable because the cross-encoder runs on only the short list, not on the whole corpus. Most of the latency stays in the first-stage retrieval.

## What the cross-encoder sees
Feed the model the raw query and the raw chunk text. Do not include the contextual prefix that was added only for embedding; the cross-encoder benefits from seeing the original sentence or paragraph. If the chunk is long, truncate it to the model’s practical input size rather than letting it overflow.

Store the cross-encoder score alongside the original retrieval score so you can inspect both. In many cases a simple weighted combination or even the cross-encoder score alone is enough for the final order.

```python
def rerank(query, candidates, top_k=5):
    pairs = [(query, c.text) for c in candidates]
    scores = cross_encoder.predict(pairs)  # higher is better
    ranked = sorted(
        zip(candidates, scores),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [c for c, _ in ranked[:top_k]]
```

## Where it sits in the pipeline
Run the cross-encoder after the hybrid or vector search and before the context is assembled for the language model. A typical flow is: embed the query, retrieve 50 candidates, rerank to the top 5 or 8, then build the prompt from those. If you also do sentence-level retrieval, rerank the sentences first, then optionally collapse back to posts if the UI shows post-level results.

Cache nothing by default. Query and chunk pairs change often enough that a cache helps only for repeated identical questions. Measure first; the reranker is usually fast enough on a few dozen pairs.

## Choosing and evaluating the model
Small cross-encoders (a few hundred million parameters) are sufficient for most documentation and blog corpora. Larger models give higher accuracy at higher latency and cost. Start with a well-known small model and compare it against your current retrieval order on a set of real questions.

Look at two numbers: how often the correct passage moves into the top three, and how much the end-to-end answer improves. If the reranker rarely changes the order, the first-stage retrieval may already be strong enough or the candidate set may be too small.

## What good looks like
A question whose best answer was previously ranked fourth or fifth now appears first or second after reranking. The language model receives tighter context and produces fewer off-target replies. End-to-end latency grows by only a small, predictable amount. If the reranker consistently pushes relevant chunks down, or if its latency exceeds the savings from sending fewer tokens to the language model, the model choice or the candidate cutoff needs another look.