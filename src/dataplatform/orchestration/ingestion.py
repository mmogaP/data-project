"""Builds one daily-partitioned Dagster asset per (client, source) from client.yml."""

from datetime import date, timedelta

import dagster as dg

from dataplatform.config import ClientConfig, SourceConfig
from dataplatform.connectors import get_connector
from dataplatform.storage import write_partition


def raw_asset_key(client_id: str, source_name: str) -> dg.AssetKey:
    return dg.AssetKey([client_id, "raw", source_name])


def build_ingestion_asset(client: ClientConfig, source: SourceConfig) -> dg.AssetsDefinition:
    @dg.asset(
        key=raw_asset_key(client.client_id, source.name),
        group_name=client.client_id,
        partitions_def=dg.DailyPartitionsDefinition(
            start_date=source.start_date.isoformat(), timezone=client.timezone
        ),
        kinds={"python", "parquet"},
        description=f"Raw `{source.connector}` extract for {client.display_name}, one file per day.",
        owners=["team:data-platform"],
        tags={"client": client.client_id, "layer": "raw"},
        backfill_policy=dg.BackfillPolicy.single_run(),
        retry_policy=dg.RetryPolicy(max_retries=2, delay=60, backoff=dg.Backoff.EXPONENTIAL),
    )
    def _ingest(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
        connector = get_connector(source.connector, **source.params)
        rows_by_day = {}
        # One run can cover many days (backfills); each day is still its own idempotent file.
        for key in context.partition_keys:
            day = date.fromisoformat(key)
            uri, rows = write_partition(
                client.client_id, source.name, day, connector.extract(day), connector.schema
            )
            context.log.info(f"Wrote {rows} rows to {uri}")
            rows_by_day[key] = rows
        return dg.MaterializeResult(
            metadata={
                "row_count": sum(rows_by_day.values()),
                "rows_by_day": rows_by_day,
                "min_day_rows": min(rows_by_day.values()),
            }
        )

    return _ingest


def build_freshness_check(client: ClientConfig, source: SourceConfig) -> dg.AssetChecksDefinition:
    """Fails when a source hasn't landed new data within its SLA from client.yml."""
    return dg.build_last_update_freshness_checks(
        assets=[raw_asset_key(client.client_id, source.name)],
        lower_bound_delta=timedelta(hours=source.freshness_sla_hours),
    )[0]
