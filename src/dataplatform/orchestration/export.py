"""Publishes each client's marts as the JSON the dashboard is built from."""

import dagster as dg

from dataplatform.config import ClientConfig
from dataplatform.export import export_client

# The marts the dashboard reads; the export runs after dbt rebuilds them.
MART_MODELS = ["fct_complaints", "mart_complaints_daily", "mart_company_scorecard"]


def build_export_asset(client: ClientConfig) -> dg.AssetsDefinition:
    @dg.asset(
        key=dg.AssetKey([client.client_id, "dashboard_data"]),
        group_name=client.client_id,
        deps=[dg.AssetKey([client.client_id, model]) for model in MART_MODELS],
        partitions_def=dg.DailyPartitionsDefinition(
            start_date=client.start_date.isoformat(), timezone=client.timezone
        ),
        backfill_policy=dg.BackfillPolicy.single_run(),
        kinds={"json"},
        description=f"Aggregates for the {client.display_name} dashboard, served from the edge.",
        owners=["team:data-platform"],
        tags={"client": client.client_id, "layer": "serving"},
    )
    def _export(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
        # Marts cover the whole history, so the export is a full snapshot on every run.
        path, payload = export_client(client)
        context.log.info(f"Wrote {path}")
        return dg.MaterializeResult(
            metadata={
                "path": dg.MetadataValue.path(str(path)),
                "complaints": payload["kpis"]["complaints"],
                "days_covered": payload["kpis"]["days_covered"],
                "latest_partition": str(payload["pipeline"]["latest_partition"]),
                "freshness_status": payload["pipeline"]["status"],
            }
        )

    return _export
