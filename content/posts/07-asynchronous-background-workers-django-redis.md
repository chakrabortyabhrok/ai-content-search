---
title: Asynchronous Background Workers with Django and Redis
category: Backend
status: published
---
## Why the request must return fast
A Django view that waits for an embedding call, a large file parse, or a third-party API will eventually time out or block other users. The view’s only job is to accept the request, record that work is needed, and return a response. Everything slow moves to a background worker.

Redis acts as the broker. The web process pushes a small message onto a Redis list. A separate worker process, running in its own container or on its own machine, pulls that message and does the real work. The user sees an immediate “accepted” or “queued” reply. Later they can poll a status endpoint or receive a notification when the job finishes.

## What gets stored in the queue
Keep the message tiny. Store only the primary key of the object that needs processing and the name of the task. Do not put the full post body, the file contents, or any large payload in Redis. The worker loads what it needs from Postgres using that primary key. This keeps Redis memory low and avoids duplicating data that already lives in the database.

Each task should be idempotent. Running it twice on the same object must produce the same result and must not create duplicate rows or duplicate external API calls. The same discipline used for the sentence indexer applies here. Check a status or a hash before doing expensive work.

```python
# views.py
def reindex_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.status = "queued"
    post.save(update_fields=["status"])
    # only the id goes to the queue
    enqueue_task("reindex_sentences", post.id)
    return JsonResponse({"status": "queued"})
```

## Worker process and retries
Run the worker as its own long-lived process. In Docker Compose it is a separate service that uses the same image as the web app but a different command. It shares the database and Redis connection settings through environment variables.

Configure automatic retries with exponential back-off for transient failures such as network blips or temporary rate limits. After a small number of retries the task should land in a dead-letter queue or be marked failed in the database so a human can inspect it. Silent infinite retries hide problems.

## Visibility and cleanup
Every job needs a status the application can read: pending, running, succeeded, failed. Store that status on the model or in a lightweight job table. The view that originally queued the work can then show progress without asking Redis directly.

Old successful job records can be deleted after a few days. Failed jobs should be kept longer so you can see patterns. Redis itself needs a max-memory policy so a sudden spike of messages does not fill the disk. A simple volatile-lru or allkeys-lru policy is enough for most task queues.

## What good looks like
A user clicks “re-index” and receives a response in under two hundred milliseconds. The worker picks up the job within a second and finishes without blocking any web request. If the same button is clicked twice quickly, only one indexing run occurs. When a third-party embedding service is briefly down, the job retries a few times and then surfaces a clear failure instead of disappearing. If the web process ever waits on the worker, or if large payloads are written into Redis, the boundary has been crossed and needs to be restored.