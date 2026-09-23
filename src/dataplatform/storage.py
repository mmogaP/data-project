"""Raw landing zone.

Layout: {RAW_ROOT}/{client}/{source}/ds=YYYY-MM-DD/data.parquet

One file per (client, source, day). Re-running a day overwrites its file, so every
ingestion run is idempotent and backfills are just re-runs. RAW_ROOT can be a local
path or a gs:// URI; pyarrow resolves the filesystem from it.
"""

import os
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import fs

from dataplatform.config import REPO_ROOT


def raw_root() -> str:
    root = os.environ.get("RAW_ROOT", "data/raw")
    if "://" in root:
        return root
    path = Path(root)
    return str(path if path.is_absolute() else REPO_ROOT / path)


def warehouse_root() -> str:
    """Where per-client DuckDB warehouses live (dbt's dev target)."""
    root = os.environ.get("WAREHOUSE_ROOT", "data/warehouse")
    path = Path(root)
    return str(path if path.is_absolute() else REPO_ROOT / path)


def partition_path(client_id: str, source: str, day: date, root: str | None = None) -> str:
    return f"{root or raw_root()}/{client_id}/{source}/ds={day.isoformat()}/data.parquet"


def write_partition(
    client_id: str,
    source: str,
    day: date,
    records: Iterable[dict],
    schema: pa.Schema,
    root: str | None = None,
) -> tuple[str, int]: #return type is a tuple of string and int
    """Write one day of records, replacing any previous file. Returns (uri, row_count)."""
    ingested_at = datetime.now(UTC)
    full_schema = schema.append(pa.field("_ingested_at", pa.timestamp("us", tz="UTC")))
    rows = [{**r, "_ingested_at": ingested_at} for r in records]
    table = pa.Table.from_pylist(rows, schema=full_schema)

    uri = partition_path(client_id, source, day, root)
    filesystem, path = fs.FileSystem.from_uri(uri)
    filesystem.create_dir(path.rsplit("/", 1)[0], recursive=True)

    if isinstance(filesystem, fs.LocalFileSystem):
        # Write then rename so readers never see a half-written file.
        tmp = f"{path}.tmp"
        pq.write_table(table, tmp, filesystem=filesystem)
        filesystem.move(tmp, path)
    else:
        pq.write_table(table, path, filesystem=filesystem)

    return uri, table.num_rows
