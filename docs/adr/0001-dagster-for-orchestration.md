# 0001 — Dagster for orchestration

**Status:** accepted

## Context

The platform needs scheduling, retries, dependency ordering between ingestion and dbt, and
reliable backfills for many clients. Main options: Airflow (Cloud Composer on GCP), Dagster,
Prefect.

## Decision

Dagster, modelling every table as a daily-partitioned **asset**.

- `dagster-dbt` turns each dbt model into an asset and each dbt test into an asset check, so
  ingestion and transformation form one lineage graph without hand-written task wiring.
- Partitions make backfills a first-class operation (select a date range in the UI), and the
  single-run backfill policy runs dbt once for the whole range.
- Assets are generated from `client.yml`, which fits the "one codebase, many clients" model.
- Cost: Cloud Composer starts around USD 300+/month. Dagster OSS can run on a small VM or
  Cloud Run.

## Consequences

- Less common than Airflow in job postings; the concepts (DAGs, retries, sensors, backfills)
  map directly, and dbt + Airflow via Astronomer Cosmos would be the equivalent there.
- Needs a persistent Dagster instance (Postgres) once deployed; locally `dagster dev` suffices.
