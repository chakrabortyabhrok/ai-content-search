---
title: Advanced Database Indexing for Django Search
category: Performance
status: published
---
## Indexes are query plans
An index is useful only when the database can use it for the exact query you run. A B-tree on a title column speeds up `title__icontains` only if the planner chooses it. A GIN index on a tsvector column speeds up full-text search. A pgvector HNSW index speeds up distance ordering. Adding indexes without looking at the queries that will use them wastes space and slows every write.

Start by logging the slow queries. Django Debug Toolbar or the database’s own slow-query log shows which lookups take the longest. Then create the smallest index that matches those lookups. After the index exists, run `EXPLAIN ANALYZE` again to confirm the planner actually uses it.

## Full-text and trigram indexes
Postgres full-text search needs a tsvector column and a GIN index. Django can maintain the tsvector with a generated column or with a trigger. Once the index is in place, `SearchVector` and `SearchQuery` become fast even on tens of thousands of posts.

For shorter fields such as titles or tags, a trigram index (pg_trgm) helps `icontains` and similarity searches. The index is larger than a normal B-tree, so add it only to columns that are actually searched with partial matches.

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(name="title_trgm", fields=["title"], opclasses=["gin_trgm_ops"]),
        ]
```

## Vector indexes and filtering
When you also store embeddings, the HNSW index handles the distance sort. Combine it with ordinary B-tree indexes on the columns you filter first. A query that filters by status and category, then orders by vector distance, can use the B-tree indexes to shrink the set and the HNSW index only on the remaining rows. The order of filters in the Django queryset matters; put the most selective filters first.

Partial indexes are useful when only published posts are ever searched. An index with a `WHERE status = 'published'` clause stays smaller and faster than an index on every row.

## Maintenance and write cost
Every index slows inserts and updates. After a large import, run `ANALYZE` so the planner has fresh statistics. Rebuild a GIN or HNSW index during low-traffic hours if it becomes bloated. Monitor index size; an unused index that occupies hundreds of megabytes should be dropped.

Django migrations that add indexes should use `atomic = False` for the large ones so they do not hold an exclusive lock for the whole build. Postgres can build many indexes concurrently.

## What good looks like
A search for a rare phrase returns in tens of milliseconds and the `EXPLAIN` plan shows an index scan, not a sequential scan. Adding a new filter does not force a full table read. Write latency stays acceptable after the extra indexes are added. If a common search still shows a sequential scan, or if an index exists but is never chosen by the planner, the index definition or the query shape needs another look.