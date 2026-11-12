---
title: Automated Backup and Disaster Recovery for Docker Postgres
category: Operations
status: published
---
## Backups must leave the host
A Postgres volume that lives only on the same disk as the container is not a backup. If the disk fails or the volume is removed by mistake, the data is gone. An automated backup copies the database to a different machine or to object storage on a schedule, then verifies that the copy can be restored.

For a Docker Compose setup the simplest reliable method is `pg_dump` run from a short-lived container or from a cron job on the host. The dump is compressed and uploaded. WAL archiving or base backups are better once the database grows large, but a nightly logical dump is enough for most solo or small-team projects.

## A minimal dump script
The script connects to the Postgres service, writes a custom-format dump, and uploads it. Use the same network as the Compose file so the hostname `postgres` resolves. Store credentials in environment variables or a secrets file that the cron job can read. Keep the last seven daily dumps and one weekly dump; delete older files automatically.

Test the script by hand before trusting the schedule. A backup that has never been restored is only a hope.

```bash
#!/bin/bash
set -euo pipefail
STAMP=$(date +%Y%m%d-%H%M)
docker compose exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" \
  > "/backups/db-$STAMP.dump"
# upload /backups/db-$STAMP.dump to object storage
find /backups -name 'db-*.dump' -mtime +7 -delete
```

## Restore procedure
Document the restore steps while the system is healthy. A typical recovery creates a fresh Postgres container, copies the dump file in, and runs `pg_restore`. Because the dump is in custom format it can restore a single table if needed, or the whole database.

Practice the restore on a separate Compose project or a cheap VPS at least once a quarter. Time how long it takes. Note any manual steps such as re-creating extensions or resetting sequences. Update the document if the steps change.

## Point-in-time and verification
If you enable WAL archiving, you can recover to a moment just before an accidental deletion. For many projects the extra operational cost is not worth it until the data volume or the rate of change justifies the work. A nightly dump plus a short recovery-time objective is a clearer trade-off.

After every backup, run a quick verification: restore the newest dump into a temporary database and run a simple query that checks row counts on the most important tables. Fail the backup job if the counts are zero or wildly different from the day before. This catches truncated dumps and permission problems.

## What good looks like
A nightly job produces a compressed dump, uploads it, and deletes old copies without manual intervention. A documented restore brings a new environment to a usable state in under an hour. A verification query runs automatically and alerts on failure. If the only copy of the data sits in the same Docker volume as the live database, or if no one has successfully restored a dump in the last six months, the backup process is incomplete and needs a tested off-site copy.