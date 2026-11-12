---
title: Privacy-First Analytics Pipeline with Django and Postgres
category: Analytics
status: published
---
## Collect less, aggregate early
A privacy-first analytics pipeline stores only what is needed to answer a few clear questions: which pages are viewed, which features are used, and whether an error occurred. It never stores raw IP addresses, full user-agent strings, or any identifier that can be tied back to a person after the session ends.

Events are written as short, structured rows. As soon as possible they are aggregated into daily or hourly counters. The raw events can then be deleted or partitioned away. This keeps the database small and reduces the amount of personal data that exists at any moment.

## Event shape and ingestion
Each event carries a timestamp, an event name, a page or feature identifier, and a few low-cardinality properties such as status code or content type. A session key may be included if it is rotated daily and never linked to an account. The ingestion endpoint validates the payload, rejects anything outside the allowed schema, and inserts the row with a single ORM call or a bulk insert.

Rate-limit the endpoint by IP or by a short-lived token so a malfunctioning client cannot fill the table. Return 204 immediately; do not wait for downstream processing.

```python
class AnalyticsEvent(models.Model):
    name = models.CharField(max_length=64)
    path = models.CharField(max_length=200, blank=True)
    status = models.PositiveSmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name", "created_at"]),
        ]
```

## Aggregation and retention
A nightly management command or a scheduled query groups the raw events by day, event name, and path, then writes the counts into a summary table. After the summary is written, raw events older than seven days are deleted. The summary table is kept for a year or two; it contains no identifiers, only counts.

Postgres partitioning on the raw-event table by day makes the deletion fast. Dropping an old partition is cheaper than deleting millions of rows. The summary table stays small enough for ordinary indexes.

## Queries that stay useful
Dashboards read only the summary table. Typical questions are “page views per day for the last 30 days” or “error rate by path.” Because the data is already aggregated, these queries are simple `GROUP BY` statements and return quickly.

If a more detailed investigation is required, it must happen inside the short raw-event window or be performed with a one-off, access-controlled query that is not part of the normal pipeline. No automatic join to the user table exists.

## What good looks like
A new page or feature can be tracked by sending one additional event name; no schema migration is required. Daily summaries appear automatically and raw events disappear after a week. A database dump of the analytics tables contains no IP addresses, no user ids, and no free-text fields that could identify someone. If raw events are retained indefinitely, or if the ingestion endpoint accepts arbitrary JSON that is stored as-is, the pipeline is collecting more than it needs and should be narrowed.