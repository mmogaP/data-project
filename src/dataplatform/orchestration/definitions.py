"""Dagster entry point. Everything is generated from clients/*/client.yml.

uv run dagster dev -m dataplatform.orchestration.definitions
"""

import dagster as dg

from dataplatform.config import load_clients
from dataplatform.orchestration.ingestion import build_freshness_check, build_ingestion_asset
from dataplatform.orchestration.transformation import build_dbt_assets


def build_definitions() -> dg.Definitions:
    assets, checks, jobs, schedules, resources = [], [], [], [], {}

    for client in load_clients():
        client_assets = [build_ingestion_asset(client, s) for s in client.sources]
        checks += [build_freshness_check(client, s) for s in client.sources]

        dbt_defs, dbt_resource = build_dbt_assets(client)
        client_assets.append(dbt_defs)
        resources[f"dbt_{client.client_id}"] = dbt_resource
        assets += client_assets

        # Daily job per client: ingest yesterday's partition, then run dbt on it.
        job = dg.define_asset_job(
            name=f"{client.client_id}_daily",
            selection=dg.AssetSelection.groups(client.client_id),
            tags={"client": client.client_id},
        )
        jobs.append(job)
        schedules.append(
            dg.build_schedule_from_partitioned_job(
                job,
                hour_of_day=client.schedule_hour,
                minute_of_hour=client.schedule_minute,
            )
        )

    return dg.Definitions(
        assets=assets,
        asset_checks=checks,
        jobs=jobs,
        schedules=schedules,
        sensors=[dg.build_sensor_for_freshness_checks(freshness_checks=checks)] if checks else [],
        resources=resources,
    )


defs = build_definitions()
