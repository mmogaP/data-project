"""CFPB Consumer Complaint Database.

Public API, no key required: ~28k complaints/day across all US financial companies.
https://cfpb.github.io/api/ccdb/
"""

from collections.abc import Iterator
from datetime import date

import httpx
import pyarrow as pa
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from dataplatform.connectors.base import Connector

API_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

FIELDS = [
    "complaint_id",
    "date_received",
    "date_sent_to_company",
    "product",
    "sub_product",
    "issue",
    "sub_issue",
    "company",
    "company_response",
    "company_public_response",
    "timely",
    "submitted_via",
    "state",
    "zip_code",
    "tags",
]


class CfpbComplaintsConnector(Connector):
    name = "cfpb_complaints"
    schema = pa.schema([pa.field(f, pa.string()) for f in FIELDS])

    def __init__(self, page_size: int = 10_000, timeout_seconds: float = 120, **params):
        super().__init__(**params)
        self.page_size = page_size
        self.client = httpx.Client(timeout=timeout_seconds)

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, max=60),
        reraise=True,
    )
    def _fetch_page(self, day: date, search_after: str | None) -> dict:
        params = {
            "size": self.page_size,
            "no_aggs": "true",
            # Both bounds are inclusive, so min == max selects exactly one day.
            "date_received_min": day.isoformat(),
            "date_received_max": day.isoformat(),
        }
        if search_after:
            params["search_after"] = search_after
        response = self.client.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()

    def extract(self, day: date) -> Iterator[dict]:
        search_after = None
        while True:
            hits = self._fetch_page(day, search_after)["hits"]["hits"]
            for hit in hits:
                yield {f: hit["_source"].get(f) for f in FIELDS}
            if len(hits) < self.page_size:
                return
            # The API paginates with Elasticsearch's search_after, encoded as "score_id".
            score, last_id = hits[-1]["sort"]
            search_after = f"{score}_{last_id}"
