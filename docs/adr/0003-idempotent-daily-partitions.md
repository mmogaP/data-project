# 0003 — Idempotent daily partitions as the unit of work

**Status:** accepted

## Context

Sources are re-queried, runs fail halfway, and CFPB complaints change after publication
(`company_response` moves from "In progress" to a final status within ~15 days).

## Decision

- The unit of work is one (client, source, day). Ingestion writes exactly one file per unit,
  via write-then-rename, replacing any previous version.
- `_ingested_at` is stamped on every row. Staging deduplicates on the business key and keeps the
  latest version.
- Incremental dbt models use `delete+insert` keyed on `partition_date`, limited to the window
  Dagster passes as `start_date`/`end_date` vars.
- An empty day still writes a zero-row file with the full schema, so "no data" is
  distinguishable from "not ingested".

## Consequences

- Any run or backfill can be retried safely.
- Picking up late status changes means re-materializing recent partitions. Next step: a weekly
  job that re-runs the last 14 days.
