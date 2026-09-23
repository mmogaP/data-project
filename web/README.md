# Dashboard (planned)

SvelteKit on Cloudflare Workers.

- Marts are exported after each successful dbt run to Cloudflare D1 (small aggregates) or R2
  (Parquet/JSON).
- The site reads from D1/R2 at the edge. It never queries the warehouse directly, so there are no
  cloud credentials in Workers, no per-page-view warehouse cost, and latency stays low.
- Per-client access through Cloudflare Access. Each client sees only its own data.
- An internal **Pipeline Health** page shows the last run per client, freshness against SLA, and
  test results.
