---
title: Docker Compose for Production Django and Postgres
category: Deployment
status: published
---
## One file is not enough
A single docker-compose.yml works for local development. It fails in production because it mixes secrets, volumes, restart policies, and resource limits that belong in different places. Production needs at least two files: a base compose and an override that only production uses.

The base file defines the services, networks, and health checks. The production override adds restart policies, resource limits, and the external volume for Postgres. Environment variables that change between machines stay outside the compose files. They come from a .env that is never committed.

## Postgres must outlive the container
The database volume must be named and external. If the volume is anonymous, removing the container deletes the data. An external volume survives compose down and can be backed up or moved to another host. The Postgres service should also have a health check so Django waits until the database is actually ready to accept connections.

## Django settings that matter
Gunicorn runs inside the Django container. One worker is not enough. Start with two or three workers and raise the number only after measuring memory. The container must not run as root. A non-root user and a read-only root filesystem stop many simple attacks.

Static files are collected at build time, not at runtime. The image already contains the static assets. A separate nginx container serves them and proxies dynamic requests to Gunicorn. This keeps the Django process free of file-serving work.

## What good looks like
A production compose brings the stack up with one command, survives a reboot, and keeps the database after the containers are replaced. If the data disappears when you recreate the Postgres container, the volume was never external.