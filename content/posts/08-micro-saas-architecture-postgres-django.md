---
title: Micro-SaaS Architecture with Postgres and Django
category: Architecture
status: published
---
## One app, clear boundaries
A micro-SaaS does not need microservices. A single Django project with a well-structured set of apps is easier to deploy, debug, and reason about while the product is still finding its users. The important boundary is not between servers; it is between the core domain and everything else.

Keep billing, authentication, and the main product logic in separate Django apps. The product app owns the models that customers pay for. The billing app owns subscriptions and invoices. The accounts app owns users and teams. Each app exposes a small set of functions or model methods that the others may call. Direct imports of models across these boundaries should be rare. This keeps a change in pricing from rippling through the entire codebase.

## Postgres as the single source of truth
All durable state lives in Postgres. User accounts, subscription status, usage counters, and the actual product data share one database. This removes an entire class of consistency problems. A subscription check and a feature-flag read can happen in the same transaction if needed.

Use row-level security or simple team_id foreign keys so every query is automatically scoped to the current customer. A middleware or a custom manager sets the current team at the start of the request. Forgetting the filter then becomes a loud error instead of a silent data leak. Indexes on team_id plus the columns you filter and sort by keep these queries fast even after thousands of customers.

```python
class TeamQuerySet(models.QuerySet):
    def for_team(self, team):
        return self.filter(team=team)

class Document(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    objects = TeamQuerySet.as_manager()
```

## Background work and external services
Anything that talks to Stripe, sends email, or generates a report runs in a background worker. The web process only records the intent. A successful payment webhook, for example, updates the subscription row and enqueues a task that provisions the new feature limits. If the worker is down, the database still shows the correct subscription state; the provisioning simply waits.

External service credentials and webhook secrets stay in environment variables. The code that verifies a Stripe signature or calls an embedding API lives in one module per provider. The rest of the application never sees the raw HTTP details.

## Deployment that stays boring
One Docker Compose file (or a small set of them) runs the web process, the worker, Postgres, and Redis. Static files are collected at build time and served by a reverse proxy. Database migrations run as an explicit release step before the new web containers start. There is no separate “migration service.”

Backups are a nightly pg_dump or a managed Postgres snapshot stored outside the application servers. Restoring to a new environment should be a documented, tested procedure, not an emergency invention.

## What good looks like
A new customer can sign up, pay, and use the core feature without any manual step. Adding a second product surface (an API, a new dashboard page) requires changes in only the product app and its templates or serializers. If a pricing change forces edits in five different apps, or if customer data can be queried without a team filter, the boundaries have blurred and need to be tightened before the next feature.