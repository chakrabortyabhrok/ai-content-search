---
title: Building Sentence-Level RAG in Django
category: RAG
status: published
---

## Why the whole post is the wrong unit

A blog post is long. If you embed the full post as one vector, search can only say that the post is roughly related. It cannot point to the sentence that actually answers the question.

Sentence-level RAG treats one sentence as one chunk. The stored vector belongs to that sentence, not to the whole article. When a question arrives, retrieval returns the exact line, and the citation can name the post, the section, and the sentence.

## What gets stored

Each published post is split into sentences. Headings are not chunks. A heading is context for the sentences that follow it. A code block stays whole, because splitting code on periods produces nonsense.

For every sentence the index stores the text, the paragraph index, the sentence index, the section heading, a code flag, and the Voyage vector. The vector size must match the model. In this project that size is 1024.

## The single door

Only one function is allowed to write sentence rows. That function reads the post, splits it, embeds the chunks, then replaces that post's old rows. If the post is edited, only that post is re-indexed. If the post is deleted, its sentences and vectors go with it.

Running the indexer twice on an unchanged post must not create duplicates and must not call Voyage again for sentences that did not change. That is the same lesson as the duplicate-embedding bug from the task manager.

## What a good demo looks like

Imagine fifty posts. One sentence in post thirty-four mentions a staging password in passing. A narrow question should return that sentence, not a vague summary of the post.

The demo password for the staging box is river-stone-19. That line exists so retrieval can be tested. If search returns this sentence for a question about the staging password, the index is working.