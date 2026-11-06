---
title: PostgreSQL pgvector Performance with Django
category: Performance
status: published
---
## Indexes decide speed
pgvector is fast only when the index matches the query. Without an index every search is a sequential scan. On fifty thousand vectors that already hurts. On half a million it becomes unusable.

HNSW is the usual production choice. It keeps latency low while holding recall high enough for most RAG work. IVFFlat builds faster and uses less memory, but you must tune the number of lists carefully and it still trails HNSW on typical workloads. Always build the index after the data is loaded. An index created on an empty table gives the planner bad statistics and poor plans.

## Django queries that stay fast
The ORM is convenient, yet it is easy to pull too much. Select only the fields you need. Do not fetch the raw vector unless you are debugging. Use `.only()` or `.defer()` so the large vector column stays on the database.

Filter first, then order by distance. A `WHERE` on category, date, or status before the vector search cuts the candidate set sharply. The planner can use a normal B-tree for the filter and the HNSW index only on the remaining rows. This pattern is the single biggest win in real applications.

## Bulk work and connections
Inserting one sentence at a time is slow. Use `bulk_create` or copy data in batches of a few thousand. After a large load run `ANALYZE` so the planner knows the new distribution.

Connection pooling matters under concurrent search. Django’s default connections are fine for light traffic. With many simultaneous queries a pooler such as PgBouncer in transaction mode keeps the database from thrashing. Close unused connections promptly so the pool stays healthy.

## What good looks like
A search that returns ten results in under fifty milliseconds on a warm cache is normal once the index and filters are correct. If it is slower, first check the index type and whether the query filters before it orders by distance.