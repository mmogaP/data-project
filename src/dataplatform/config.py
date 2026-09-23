"""Client configuration.

Each client lives in `clients/<client_id>/client.yml`. Onboarding a new client means
adding that file plus a dbt project; the orchestration layer builds assets from it.
"""

from datetime import date
from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENTS_DIR = REPO_ROOT / "clients"


class SourceConfig(BaseModel):
    name: str
    connector: str
    start_date: date
    freshness_sla_hours: int = 48
    # write like this so every object gets its own dictionary
    # instead of sharing the same one across all instances
    params: dict = Field(default_factory=dict)


class ClientConfig(BaseModel):
    client_id: str
    display_name: str
    industry: str
    enabled: bool = True
    # Daily run time, in `timezone`. Each run processes the previous day's partition.
    schedule_hour: int = 7
    schedule_minute: int = 0
    timezone: str = "America/New_York"
    dbt_project_dir: str = "dbt"
    sources: list[SourceConfig] = Field(default_factory=list)

    @property
    def path(self) -> Path:
        return CLIENTS_DIR / self.client_id

    @property
    def dbt_path(self) -> Path:
        return self.path / self.dbt_project_dir

    @property
    def start_date(self) -> date:
        return min(s.start_date for s in self.sources)


def load_client(path: Path) -> ClientConfig:
    # it loads safe_load as safety measures
    return ClientConfig.model_validate(yaml.safe_load(path.read_text()))


@cache #cache of current clients so we don't have to reload them every time we call this function
def load_clients(include_disabled: bool = False) -> tuple[ClientConfig, ...]:
    clients = [load_client(p) for p in sorted(CLIENTS_DIR.glob("*/client.yml"))]
    return tuple(c for c in clients if c.enabled or include_disabled)
