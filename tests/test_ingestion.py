from datetime import date

import httpx
import pyarrow.parquet as pq
import respx

from dataplatform.config import load_clients
from dataplatform.connectors import get_connector
from dataplatform.connectors.cfpb import API_URL
from dataplatform.storage import write_partition


def _hit(complaint_id: str) -> dict:
    return {
        "_source": {"complaint_id": complaint_id, "company": "ACME BANK", "timely": "Yes"},
        "sort": [1.0, complaint_id],
    }


@respx.mock
def test_cfpb_paginates_with_search_after():
    route = respx.get(API_URL).mock(
        side_effect=[
            httpx.Response(200, json={"hits": {"hits": [_hit("3"), _hit("2")]}}),
            httpx.Response(200, json={"hits": {"hits": [_hit("1")]}}),
        ]
    )
    connector = get_connector("cfpb_complaints", page_size=2)

    records = list(connector.extract(date(2026, 9, 1)))

    assert [r["complaint_id"] for r in records] == ["3", "2", "1"]
    assert route.calls[1].request.url.params["search_after"] == "1.0_2"
    assert route.calls[0].request.url.params["date_received_min"] == "2026-09-01"
    assert route.calls[0].request.url.params["date_received_max"] == "2026-09-01"
    # Every schema field is present even when the API omits it.
    assert set(records[0]) == set(connector.schema.names)


def test_write_partition_is_idempotent(tmp_path):
    connector = get_connector("cfpb_complaints")
    day = date(2026, 9, 1)
    row = {name: None for name in connector.schema.names} | {"complaint_id": "1"}

    write_partition("acme", "cfpb_complaints", day, [row, row], connector.schema, root=str(tmp_path))
    uri, rows = write_partition("acme", "cfpb_complaints", day, [row], connector.schema, root=str(tmp_path))

    assert rows == 1
    assert pq.read_table(uri).num_rows == 1
    assert uri.endswith("acme/cfpb_complaints/ds=2026-09-01/data.parquet")


def test_empty_day_still_writes_a_file(tmp_path):
    connector = get_connector("cfpb_complaints")
    uri, rows = write_partition("acme", "src", date(2026, 1, 1), [], connector.schema, root=str(tmp_path))

    assert rows == 0
    assert "_ingested_at" in pq.read_schema(uri).names


def test_client_configs_reference_known_connectors():
    from dataplatform.connectors import REGISTRY

    for client in load_clients(include_disabled=True):
        for source in client.sources:
            assert source.connector in REGISTRY, f"{client.client_id}.{source.name}"
