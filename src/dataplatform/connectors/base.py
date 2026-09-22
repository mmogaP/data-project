from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import date
from typing import ClassVar

import pyarrow as pa


class Connector(ABC):
    """Extracts one day of records from a source.

    Connectors know nothing about clients or storage: they receive params from
    client.yml and yield dicts matching `schema`.
    """

    name: ClassVar[str]
    schema: ClassVar[pa.Schema]

    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def extract(self, day: date) -> Iterator[dict]: ...
