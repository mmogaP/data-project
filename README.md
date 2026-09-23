# Data Platform

A multi-client data platform, built the way an outsourced data team would run it: one shared
codebase, one config file and one dbt project per client, orchestrated end to end.

Today it runs **Hudson Community Bank** (fictional banking client) on real public data from the
[CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)
(~28k complaints/day). **Empire Health Network** (healthcare) is next.

```
clients/<client>/client.yml
        │
        ▼
┌──────────────┐   ┌──────────────────────────┐   ┌─────────────────────────────────┐   ┌──────────────┐
│  Connectors  │──▶│  Raw landing zone        │──▶│  dbt (per client)               │──▶│  Dashboard   │
│  (Python)    │   │  ds=YYYY-MM-DD/*.parquet │   │  staging → facts → marts        │   │  JSON export │
└──────────────┘   │  local  →  GCS           │   │  DuckDB  →  BigQuery            │   │  SvelteKit   │
                   └──────────────────────────┘   └─────────────────────────────────┘   │  Cloudflare  │
                                                                                         └──────────────┘
        └──────────────────────── Dagster: daily partitions, backfills, schedules, checks ─┘
```

## What it demonstrates

| Concern | How |
|---|---|
| **Onboarding a client** | Add `clients/<id>/client.yml` + a dbt project. Assets, jobs and schedules are generated from config. |
| **Idempotency** | One Parquet file per (client, source, day), overwritten atomically on re-run. |
| **Backfills** | Daily partitions with a single-run backfill policy: 30 days = 1 run, not 30. |
| **Incremental models** | `fct_complaints` rebuilds only the partition window Dagster passes in (`delete+insert`). |
| **Late-arriving updates** | Complaints change status after publication; staging keeps the latest ingested version. |
| **Data quality** | dbt tests surface as Dagster asset checks; source freshness SLA per client; shared generic tests. |
| **PII** | Shared `dbt_core` package: ZIP truncated to 3 digits, salted hashing for direct identifiers. |
| **Client isolation** | Assets namespaced `client/…`, separate warehouse per client (dataset per client in BigQuery). |

## Quickstart

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
(cd clients/hudson_bank/dbt && uv run dbt deps --profiles-dir .)

# UI at http://localhost:3000 — select the hudson_bank group and materialize a partition
uv run dagster dev

# or from the CLI: backfill a range in one run
uv run dagster asset materialize -m dataplatform.orchestration.definitions \
  --select 'group:hudson_bank' --partition-range 2026-09-01...2026-09-05
```

Query the result:

```bash
uv run python -c "import duckdb; print(duckdb.connect('data/warehouse/hudson_bank.duckdb').sql('from main_marts.mart_company_scorecard order by complaint_volume_rank limit 10'))"
```

Dashboard:

```bash
cd web && pnpm install && pnpm run dev     # http://localhost:5173
```

Tests and lint: `uv run pytest` · `uv run ruff check` · `cd web && pnpm run check`

## Layout

```
clients/
  hudson_bank/          client.yml + dbt project (staging, marts, tests)
  empire_health/        healthcare client (planned)
packages/dbt_core/      shared dbt macros: PII masking, generic tests
src/dataplatform/
  config.py             client.yml schema (pydantic)
  connectors/           source extractors, registered by name
  storage.py            partitioned raw landing zone (local or gs://)
  orchestration/        Dagster assets, dbt integration, jobs, schedules
infra/terraform/        GCP + Cloudflare infrastructure (planned)
web/                    SvelteKit dashboard on Cloudflare (prerendered)
docs/adr/               architecture decisions
```

## Roadmap

- [x] Config-driven ingestion, partitioned raw zone, CFPB connector
- [x] dbt project with incremental facts, marts, shared package and tests
- [x] Dagster: partitions, single-run backfills, schedules, freshness checks
- [ ] Healthcare client: Synthea (FHIR), openFDA, NY SPARCS
- [ ] BigQuery `prod` target + GCS raw zone, Terraform
- [ ] CI: dbt slim CI on PRs (`state:modified+`), deploy on merge
- [x] Export marts to JSON; prerendered SvelteKit dashboard on Cloudflare
- [ ] Per-client access on the dashboard (Cloudflare Access)
- [ ] Pipeline health page and alerting
