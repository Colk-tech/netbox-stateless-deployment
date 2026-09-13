# NetBox Deployment

Portable, stateless NetBox deployment using Docker Compose and external managed services.

This repository contains the deployment configuration for running NetBox application nodes without persistent local application state. Application nodes are intended to be disposable and reproducible across Docker-compatible hosts.

## Architecture

Persistent state is kept outside the NetBox application nodes.

```text
                        Clients
                           │
                           ▼
                    Reverse Proxy
                    / Tunnel Layer
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       NetBox App Node             NetBox App Node
       ───────────────             ───────────────
       NetBox / Django             NetBox / Django
       Application Server          Application Server
       Background Worker           Background Worker
       Plugins                     Plugins
             │                           │
             └─────────────┬─────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         PostgreSQL   Redis-compatible   S3-compatible
                         service           storage
```

Application nodes contain only reproducible application components and configuration.

Persistent state is delegated to:

- PostgreSQL for the NetBox database
- A Redis-compatible service for background tasks and caching
- S3-compatible object storage for persistent file storage

## Current Infrastructure

The deployment is provider-independent, but the current environment uses:

| Service | Current provider |
| --- | --- |
| PostgreSQL | Supabase |
| Redis-compatible service | Aiven for Valkey |
| S3-compatible object storage | Cloudflare R2 |
| Application runtime | Docker |
| Virtualization | Proxmox VE |

Provider-specific configuration is intentionally kept out of the application architecture.

## Deployment Model

NetBox application nodes are treated as disposable compute resources.

A failed or replaced node should not require restoration of local application data. A replacement node should be deployable from this repository and the corresponding runtime secrets.

The intended recovery model is:

```text
Node failure
    │
    ▼
Remaining replica continues serving traffic
    │
    ▼
Create replacement Docker host or container
    │
    ▼
Clone repository
    │
    ▼
Provide environment secrets
    │
    ▼
docker compose up -d
    │
    ▼
Replica capacity restored
```

No persistent Docker volumes are required for NetBox application data.

## Repository Layout

```text
.
├── .env.example
├── .gitignore
├── compose.yaml
├── configuration/
│   └── extra.py
├── LICENSE
└── README.md
```

### `compose.yaml`

Defines the NetBox application and background worker containers.

It also maps the provider-independent environment variables used by this repository to the environment variables expected by the NetBox container image.

### `configuration/extra.py`

Contains additional NetBox configuration not provided directly by the upstream container configuration.

This currently includes the S3-compatible storage backend configuration.

### `.env.example`

Documents the runtime configuration interface.

Environment variable names are intentionally provider-independent:

- `PSQL_*` for PostgreSQL
- `REDIS_TASKS_*` for the task queue
- `REDIS_CACHE_*` for caching
- `S3_*` for S3-compatible object storage
- `NETBOX_*` for NetBox-specific configuration

The actual `.env` file contains secrets and must never be committed.

## Requirements

- Docker Engine
- Docker Compose v2
- Reachable PostgreSQL service
- Reachable Redis-compatible service
- Reachable S3-compatible object storage
- IPv4 or IPv6 connectivity appropriate for the configured external services

## Configuration

Create the local environment file:

```sh
cp .env.example .env
chmod 600 .env
```

Edit `.env` and provide the required credentials and endpoints.

At minimum, configure:

```text
NETBOX_*
PSQL_*
REDIS_TASKS_*
REDIS_CACHE_*
S3_*
```

Secrets must not be committed to Git.

## Start

Validate the Compose configuration:

```sh
docker compose config --quiet
```

Pull the required images:

```sh
docker compose pull
```

Start the deployment:

```sh
docker compose up -d
```

Inspect container state:

```sh
docker compose ps
```

Follow NetBox logs:

```sh
docker compose logs -f netbox
```

Follow worker logs:

```sh
docker compose logs -f netbox-worker
```

## Stop

Stop and remove the local application containers:

```sh
docker compose down
```

Because persistent application state is stored externally, application nodes are expected to be safely replaceable.

## Administrative Operations

Create a NetBox superuser:

```sh
docker compose exec netbox \
  /opt/netbox/venv/bin/python \
  /opt/netbox/netbox/manage.py \
  createsuperuser
```

Open a Django shell:

```sh
docker compose exec netbox \
  /opt/netbox/venv/bin/python \
  /opt/netbox/netbox/manage.py \
  shell
```

Open a PostgreSQL shell through NetBox:

```sh
docker compose exec netbox \
  /opt/netbox/venv/bin/python \
  /opt/netbox/netbox/manage.py \
  dbshell
```

## Security

The following principles apply to this deployment:

- Secrets are supplied at runtime and are never committed.
- PostgreSQL uses a dedicated NetBox login role.
- PostgreSQL administrative and unrelated Supabase features are not required by NetBox.
- Redis-compatible services should use TLS and authentication when supported.
- S3-compatible object storage should remain private unless public access is explicitly required.
- Application nodes should not contain authoritative persistent state.
- `SECRET_KEY` and other cluster-wide secrets must be identical across all replicas.
- External services should be accessed over encrypted connections.

## Portability

The deployment is intentionally not tied to any specific infrastructure provider.

For example:

```text
PostgreSQL
Supabase
    ↓
Aiven / RDS / Cloud SQL / self-hosted PostgreSQL

Redis-compatible
Aiven for Valkey
    ↓
Valkey / Redis / ElastiCache / other compatible service

S3-compatible storage
Cloudflare R2
    ↓
AWS S3 / MinIO / other compatible object storage
```

Changing providers should primarily require updating runtime configuration rather than changing the NetBox application deployment.

## License

Licensed under the Apache License, Version 2.0. See [`LICENSE`](./LICENSE).
