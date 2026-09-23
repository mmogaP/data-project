"""Exports each client's marts to a JSON file the dashboard bundles at build time.

The dashboard never queries the warehouse: it serves small pre-aggregated JSON from
the edge, so there are no warehouse credentials in Cloudflare and no per-view cost.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from dataplatform.config import REPO_ROOT, ClientConfig
from dataplatform.storage import warehouse_root

WEB_DATA_DIR = REPO_ROOT / "web" / "src" / "lib" / "data"
TOP_COMPANIES = 12

KPIS = """
select
    count(*)                                        as complaints,
    count(distinct company_name)                    as companies,
    count(distinct received_date)                   as days_covered,
    round(avg(case when is_timely_response then 1.0 else 0.0 end), 4) as timely_rate,
    round(avg(days_to_company), 2)                  as avg_days_to_company,
    min(received_date)                              as first_date,
    max(received_date)                              as last_date
from main_marts.fct_complaints
"""

DAILY = """
select
    received_date                   as date,
    sum(complaints)                 as complaints,
    sum(timely_responses)           as timely
from main_marts.mart_complaints_daily
group by received_date
order by received_date
"""

TOP_COMPANIES_SQL = f"""
select
    company_name                    as company,
    complaints,
    market_share_of_complaints_pct  as share_pct,
    round(timely_response_rate, 4)  as timely_rate
from main_marts.mart_company_scorecard
order by complaint_volume_rank
limit {TOP_COMPANIES}
"""

PRODUCTS = """
select
    product,
    sum(complaints) as complaints
from main_marts.mart_complaints_daily
group by product
order by complaints desc
"""

# Freshness as the dashboard reports it: how old the newest ingested row is.
PIPELINE = """
select
    max(_ingested_at)                                                as last_ingested_at,
    max(partition_date)                                              as latest_partition,
    round(date_diff('minute', max(_ingested_at), now()) / 60.0, 1)   as hours_since_ingest
from main_marts.fct_complaints
"""


def _rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    result = con.sql(sql)
    return [dict(zip(result.columns, row, strict=True)) for row in result.fetchall()]


def _pipeline_status(hours_since_ingest: float | None, sla_hours: int) -> str:
    if hours_since_ingest is None:
        return "critical"
    if hours_since_ingest > sla_hours:
        return "critical"
    if hours_since_ingest > sla_hours * 0.75:
        return "warning"
    return "good"


def export_client(client: ClientConfig, out_dir: Path | None = None) -> tuple[Path, dict]:
    """Read the client's marts and write <out_dir>/<client_id>.json. Returns (path, payload)."""
    db_path = Path(warehouse_root()) / f"{client.client_id}.duckdb"
    with duckdb.connect(str(db_path), read_only=True) as con:
        kpis = _rows(con, KPIS)[0]
        pipeline = _rows(con, PIPELINE)[0]
        sla_hours = max(s.freshness_sla_hours for s in client.sources)
        payload = {
            "client": {
                "id": client.client_id,
                "name": client.display_name,
                "industry": client.industry,
            },
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "kpis": kpis,
            "daily": _rows(con, DAILY),
            "top_companies": _rows(con, TOP_COMPANIES_SQL),
            "products": _rows(con, PRODUCTS),
            "pipeline": {
                **pipeline,
                "sla_hours": sla_hours,
                "status": _pipeline_status(pipeline["hours_since_ingest"], sla_hours),
            },
        }

    out_dir = out_dir or WEB_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{client.client_id}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    return path, payload
