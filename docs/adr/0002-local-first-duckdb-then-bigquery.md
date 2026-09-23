# 0002 — Local-first on DuckDB, BigQuery in production

**Status:** accepted

## Context

Iterating directly against BigQuery costs money and needs cloud setup before any model exists.

## Decision

- dbt `dev` target uses DuckDB; `prod` targets BigQuery. Same models, different adapter.
- The raw zone is Parquet with Hive-style `ds=` partitions. `RAW_ROOT` accepts a local path or a
  `gs://` URI, and pyarrow resolves the filesystem, so ingestion code doesn't change.
- SQL stays close to portable. Adapter-specific syntax (e.g. `date_diff`, `regexp_matches`)
  belongs in `dbt_core` macros when a second adapter needs it.

## Consequences

- Anyone can clone and run the full pipeline with no credentials.
- In BigQuery the raw zone becomes an external table (or a load job) partitioned on `ds`, and
  `fct_complaints` should be partitioned on `partition_date` and clustered on `company_name`.
- A few functions will need `adapter.dispatch` macros once `prod` is wired up.
