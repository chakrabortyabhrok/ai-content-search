---
title: PostgreSQL Connection Pooling with PgBouncer and Django
category: Performance
status: published
---
## Why Django needs a pooler
Each Django process opens its own database connections. Under a modest number of Gunicorn workers this is fine. When you add more workers, background tasks, and a few admin sessions, the total can exceed Postgres’s `max_connections`. New requests then wait or fail while the database spends time managing idle connections.

PgBouncer sits between Django and Postgres. It keeps a smaller set of real database connections open and lets many client connections share them. Django talks to PgBouncer exactly as it would talk to Postgres; only the host and port change.

## Transaction mode versus session mode
Session mode gives each client a dedicated server connection for the whole session. It is simple but saves fewer connections. Transaction mode returns the server connection to the pool as soon as the transaction ends. This is the mode that actually reduces the number of Postgres backends.

Most Django applications work in transaction mode. The main exceptions are features that rely on session-level state: temporary tables, `LISTEN/NOTIFY`, or prepared statements that must survive across transactions. If you use those, keep them on a separate connection or stay in session mode for that workload.

```ini
; pgbouncer.ini
[databases]
mydb = host=postgres port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
pool_mode = transaction
max_client_conn = 200
default_pool_size = 20
```

## Django settings that cooperate
Point Django’s `DATABASES` host and port at PgBouncer instead of at Postgres directly. Set `CONN_MAX_AGE` to 0 when using transaction mode. A persistent Django connection would hold a PgBouncer server connection longer than necessary and defeat the pool. With `CONN_MAX_AGE = 0`, Django opens a client connection, runs the request’s transactions, and closes it; PgBouncer reuses the underlying server connection for the next client.

Disable server-side cursors if you see errors about portals or prepared statements in transaction mode. Set `DISABLE_SERVER_SIDE_CURSORS = True` on the database wrapper. Most ordinary ORM queries never need them.

## Health checks and limits
Set PgBouncer’s `default_pool_size` and `max_db_connections` so the total server connections stay comfortably under Postgres’s `max_connections`. Leave headroom for admin tools and migrations that may connect directly. Monitor PgBouncer’s `SHOW POOLS` and `SHOW STATS` to see how many clients are waiting and how often server connections are created.

In Docker Compose, run PgBouncer as its own service. The web and worker containers use the PgBouncer hostname. Migrations can use the same pooled connection or a direct Postgres connection; both work as long as the migration does not rely on session state that transaction mode would clear.

## What good looks like
A traffic spike increases the number of Django workers without increasing the number of Postgres backends beyond the pool size. Idle connections disappear from `pg_stat_activity` once requests finish. Queries continue to see a consistent snapshot inside each transaction. If you observe “too many connections” errors, or if temporary tables and listen/notify stop working after the switch, the pool mode or the `CONN_MAX_AGE` setting needs to be adjusted before more workers are added.