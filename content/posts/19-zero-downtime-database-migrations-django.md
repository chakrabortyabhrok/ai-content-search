---
title: Zero-Downtime Database Migrations in Django
category: Backend
status: published
---
## Expand, then contract
A migration that rewrites a large table or adds a non-nullable column without a default will lock the table and stall requests. The safe pattern is to expand the schema first, deploy code that works with both old and new shapes, then contract the schema in a later release.

Adding a nullable column or a new table is almost always safe. Back-filling data and adding constraints happen in follow-up migrations after the new code is running. Removing a column or tightening a constraint happens only after every running process has stopped using the old shape.

## Safe column additions
Add the new column as nullable or with a database-level default. Deploy. In a data migration or a background job, fill the column for existing rows. Once every row has a value, a later migration can set the column to non-nullable. During the whole period the application code must tolerate both null and non-null values.

Renaming a column follows the same idea. Add the new column, copy data, switch the code to write both columns, deploy, back-fill, switch the code to read the new column, then drop the old column in a final migration.

```python
# migration 1 – expand
operations = [
    migrations.AddField(
        model_name="post",
        name="slug",
        field=models.SlugField(max_length=200, null=True),
    ),
]

# later migration – after back-fill
operations = [
    migrations.AlterField(
        model_name="post",
        name="slug",
        field=models.SlugField(max_length=200, unique=True),
    ),
]
```

## Indexes and long-running operations
Creating an index on a large table can lock writes. Postgres supports `CREATE INDEX CONCURRENTLY`, which does not block ordinary operations. Django migrations run inside a transaction by default, and concurrent index creation cannot run inside a transaction. Set `atomic = False` on the migration that builds the index, and use `AddIndexConcurrently` or a raw `RunSQL` statement.

The same rule applies to other long operations such as validating a new constraint. Run them outside a transaction and during a low-traffic window when possible.

## Deployment order
The application containers must be updated in an order that matches the migrations. For an expand step, run the migration first, then roll out the new code. For a contract step, roll out the code that no longer uses the old column, then run the migration that drops it. A reverse proxy or load balancer lets you keep old and new containers running together for a short time so in-flight requests finish.

Background workers must be included in the same rollout. A worker still running old code can write to a column you are about to drop.

## What good looks like
A schema change reaches production without a visible outage or a spike in error rates. Existing requests finish, new requests use the updated code, and the database never holds an exclusive lock long enough to time out queries. If a migration regularly causes connection pile-ups or forces a maintenance window, the change needs to be split into expand and contract steps before the next release.