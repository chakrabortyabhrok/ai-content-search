---
title: Contextual Retrieval Strategies with Voyage AI
category: RAG
status: published
---
## Why plain chunks lose meaning
A sentence taken out of its post often loses the subject it refers to. “It returns the exact line” is useless without knowing that “it” means the retrieval step. Contextual retrieval fixes this by prepending a short, generated description of the surrounding section or post before the chunk is embedded. The vector then carries both the local words and the larger meaning.

Voyage models respond well to this pattern because they were trained to treat the full input as a single coherent unit. A chunk that already contains its own context produces tighter similarity scores and fewer false positives than a bare sentence.

## What gets prepended
Keep the added context short and factual. A good prefix names the post title, the section heading, and one sentence that states the main point of that section. Longer prefixes waste tokens and can dilute the original chunk. The prefix is generated once, either by a small language model or by a simple template filled from the post’s metadata. It is stored with the chunk so the same text is always embedded.

For code blocks the prefix is even more important. A raw function rarely says what problem it solves. A one-line note such as “Django management command that re-indexes a single post after edit” gives the embedding model the missing intent.

```python
def build_prefixed_chunk(post, heading, sentence):
    prefix = f"Post: {post.title}. Section: {heading}. "
    return prefix + sentence
```

## Embedding and storage choices
Embed the full string (prefix + original chunk) with the Voyage model you already use. Do not embed the prefix and the chunk separately and then average them; that loses the joint meaning the model is good at capturing. Store both the original chunk and the prefixed version. Retrieval uses the prefixed vector. The original chunk is what you return to the user and what you show in citations.

Because the prefixed text is longer, watch the model’s maximum input length. Voyage’s common models accept several thousand tokens, so a short prefix plus a normal sentence or paragraph stays well inside the limit. If a chunk would overflow, drop the least important part of the prefix rather than truncating the original content.

## When to regenerate context
Regenerate the prefix only when the post’s title, headings, or overall topic change. A small wording edit inside a sentence does not require a new prefix. This keeps re-indexing cheap. The same “single door” function that writes sentence rows can also decide whether the prefix is still valid. If the heading or title hash matches the stored hash, reuse the old prefix and skip the generation step.

## What good looks like
A question about “how the indexer avoids duplicate Voyage calls” should return the exact sentence that mentions the duplicate-embedding lesson, even if that sentence never repeats the word “indexer.” The prepended context supplies the missing link. If the same question instead returns a vague summary from a different post, the prefixes are either missing or too generic and need another pass.