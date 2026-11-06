---
title: Lightweight Logging and Monitoring for a Solo Dev
category: Operations
status: published
---
## Logs you will actually read
A solo developer does not need a full observability platform. The useful goal is to answer two questions quickly: what broke, and what was the user doing when it broke. Structured logs written to stdout, plus a simple error inbox, cover most of that need.

Django’s built-in logging can write JSON lines. Each line contains a timestamp, level, logger name, message, and a few extra fields such as request path or user id. When the process runs under Docker or systemd, those lines are already collected. You can tail them, ship them to a cheap log service, or simply grep a file.

## What to log and what to skip
Log the start and end of important use-cases: a post was published, a payment webhook arrived, an indexing job failed. Include the primary key and the outcome. Do not log full request bodies, tokens, or personal data. Do not log every database query in production; that volume hides the real signals.

Errors deserve a stack trace and the request id. Warnings are for recoverable problems such as a retry that succeeded on the second attempt. Info is for the business events you may want to count later. Debug stays off in production.

```python
import logging
logger = logging.getLogger(__name__)

def publish_post(post_id, user):
    logger.info("publish_start", extra={"post_id": post_id, "user_id": user.id})
    try:
        # ... work ...
        logger.info("publish_ok", extra={"post_id": post_id})
    except Exception:
        logger.exception("publish_failed", extra={"post_id": post_id})
        raise
```

## Error tracking without a heavy agent
An unhandled exception should reach you even if you are not watching the logs. A minimal approach is to send a short message to a private Slack channel, a Discord webhook, or an email address you check. Include the exception type, the message, the path, and a link to the full log line if you have one.

Many error services have a free tier that accepts a few thousand events per month. If you use one, send only unhandled exceptions and explicit `logger.exception` calls. Ignore 404s and validation errors; they are normal traffic.

## Simple health and uptime
A health endpoint that checks the database connection and returns 200 is enough for an external uptime monitor. A free monitor can ping it every few minutes and alert you if it fails. No agent is required on the server.

For background workers, log a heartbeat or update a timestamp in the database at the end of each successful job. A small cron or a monitoring check can alert if the timestamp grows too old.

## What good looks like
When a user reports a problem you can find the matching log line in under a minute and see the post id, the user id, and the exception. An unhandled error arrives in your inbox or chat without you having to watch the server. The log volume stays low enough that you can still scroll through a day’s output. If secrets or full payloads appear in the logs, or if you learn about outages only from users, the logging and alerting rules need to be tightened.