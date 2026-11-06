---
title: Designing a Modular Blog CMS Database Schema
category: Architecture
status: published
---
## Core tables stay small
A blog CMS needs posts, authors, categories, and tags. Keeping those tables narrow makes queries fast and migrations safe. A Post row holds the title, slug, status, author id, category id, and timestamps. The body can live in the same row for simple sites or in a separate content table if you expect very large texts or multiple revisions.

Authors are ordinary users or a thin profile table linked to the user. Categories form a simple tree or a flat list. Tags are a many-to-many relation. All of these relationships use ordinary foreign keys so the database enforces integrity.

## Content and revisions
Storing every revision in the main Post table bloats the hot rows. A separate PostRevision table keeps the current post small. Each revision stores the full body, the title at that moment, and a created timestamp. The Post row points at the current revision or simply holds the latest body and lets the revision table keep history.

When a post is published, the current body is copied or marked. Drafts stay in the revision table until they are explicitly published. This pattern also makes it easy to add a “restore this version” action later.

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=20, default="draft")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(null=True, blank=True)

class PostRevision(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="revisions")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## Search and media side tables
Sentence-level search needs its own table. A Sentence row stores the text, the post id, the heading, the paragraph index, the sentence index, and the vector. It is never joined in ordinary page renders; it is used only by the retrieval path. This keeps the main Post queries light.

Media files live in a Media table with the file path, alt text, and uploader. Posts reference media through a many-to-many or a simple foreign key for a featured image. The actual files sit on disk or object storage; the database only stores the metadata.

## Indexes and constraints that matter
Unique indexes on slug and on (post, sentence index) prevent duplicates. A composite index on (status, published_at) speeds the public post list. A GIN index on the search vector and an HNSW index on the embedding column support the two search styles. Foreign keys already create indexes in most cases; add extra ones only for the filters you actually run.

## What good looks like
Publishing a post updates one row and optionally writes one revision. The public list query never touches the revision or sentence tables. Adding sentence search or media does not require altering the core Post columns. If rendering a single post regularly joins five extra tables, or if a slug collision can occur under concurrent edits, the schema boundaries or the unique constraints need to be tightened.