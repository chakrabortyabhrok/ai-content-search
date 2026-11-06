---
title: Sentence-Level Chunking Strategies for RAG
category: RAG
status: published
---
## Why sentences beat paragraphs
A paragraph often mixes several ideas. When you embed the whole paragraph, a question about one idea still returns the entire block. Sentence-level chunking stores one sentence as one vector. Retrieval can then point to the exact line that answers the question, and the citation can name the post, the section, and the sentence index.

The trade-off is more rows and more vectors. The gain is precision. For a documentation or blog corpus the extra storage is usually acceptable, and the answers become easier to verify.

## What gets split and what stays whole
Ordinary prose is split on sentence boundaries. A simple rule that looks for periods, question marks, and exclamation points followed by whitespace works for most English text. Abbreviations and decimal numbers need a short exception list so they do not create false breaks.

Headings are not chunks. A heading is stored as context for the sentences that follow it. Code blocks stay whole. Splitting code on periods produces fragments that no longer parse. Tables and lists can be kept as single chunks or split by row, depending on how users ask questions about them.

```python
import re

def split_sentences(text):
    # keep common abbreviations intact
    text = re.sub(r"\b(Mr|Mrs|Dr|e\.g|i\.e)\.", r"\1<prd>", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.replace("<prd>", ".") for p in parts if p.strip()]
```

## Metadata that travels with each sentence
Every sentence row stores the original text, the post id, the section heading, the paragraph index, the sentence index inside that paragraph, and a flag that marks code. The heading is copied onto the sentence so a later contextual prefix can be built without another lookup. The two indexes let the UI highlight the exact sentence and let the re-indexer replace only the changed sentences.

When a post is edited, only the sentences whose text or heading changed are re-embedded. Unchanged sentences keep their existing vectors. This is the same discipline that prevents duplicate embedding calls.

## Overlap and context windows
Pure sentence chunks can lose a pronoun’s referent. Two common fixes exist. The first is the contextual prefix described in earlier posts: a short note about the section is prepended before embedding. The second is a small overlap: each sentence chunk also contains the last few words of the previous sentence. Overlap increases storage a little and usually helps less than a good prefix, so start with prefixes and add overlap only if retrieval tests show missing context.

## What good looks like
A question that can be answered by one sentence returns that sentence, not the surrounding paragraph. Re-indexing an edited post touches only the changed sentences and does not call the embedding API for the rest. Code blocks appear as single chunks. If a search for a distinctive sentence returns a different sentence from the same post, or if every edit re-embeds the entire article, the chunking or the change-detection logic needs another pass.