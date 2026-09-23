"""Wraps each client's dbt project as partitioned Dagster assets."""

import json
import os
from collections.abc import Mapping
from typing import Any

import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets

from dataplatform.config import ClientConfig
from dataplatform.orchestration.ingestion import raw_asset_key
from dataplatform.storage import raw_root, warehouse_root


class ClientDbtTranslator(DagsterDbtTranslator):
    """Namespaces dbt assets by client so two clients can both have e.g. `fct_complaints`,
    and points dbt sources at the ingestion assets so lineage is one connected graph."""

    def __init__(self, client_id: str):
        super().__init__()
        self.client_id = client_id

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> dg.AssetKey:
        if dbt_resource_props["resource_type"] == "source":
            return raw_asset_key(self.client_id, dbt_resource_props["name"])
        return dg.AssetKey([self.client_id, dbt_resource_props["name"]])

    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str:
        return self.client_id


def dbt_env() -> dict[str, str]:
    """dbt runs with cwd = project dir, so hand it absolute paths."""
    return {"RAW_ROOT": raw_root(), "WAREHOUSE_ROOT": warehouse_root()}


def build_dbt_project(client: ClientConfig) -> DbtProject:
    project = DbtProject(project_dir=client.dbt_path, profiles_dir=client.dbt_path)
    os.environ.update(dbt_env())
    # In `dagster dev`, parse the project on load so model edits show up without a manual step.
    project.prepare_if_dev()
    return project


def build_dbt_assets(client: ClientConfig) -> tuple[dg.AssetsDefinition, DbtCliResource]:
    project = build_dbt_project(client)
    resource_key = f"dbt_{client.client_id}"

    @dbt_assets(
        name=f"{client.client_id}_dbt",
        manifest=project.manifest_path,
        dagster_dbt_translator=ClientDbtTranslator(client.client_id),
        partitions_def=dg.DailyPartitionsDefinition(
            start_date=client.start_date.isoformat(), timezone=client.timezone
        ),
        # A backfill of N days runs dbt once with the whole window instead of N times.
        backfill_policy=dg.BackfillPolicy.single_run(),
        required_resource_keys={resource_key},
    )
    def _dbt(context: dg.AssetExecutionContext):
        dbt: DbtCliResource = getattr(context.resources, resource_key)
        window = context.partition_time_window
        dbt_vars = {"start_date": window.start.date().isoformat(), "end_date": window.end.date().isoformat()}
        yield from dbt.cli(["build", "--vars", json.dumps(dbt_vars)], context=context).stream()

    return _dbt, DbtCliResource(project_dir=project)
