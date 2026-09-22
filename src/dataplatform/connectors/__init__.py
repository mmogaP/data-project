from dataplatform.connectors.base import Connector
from dataplatform.connectors.cfpb import CfpbComplaintsConnector

REGISTRY: dict[str, type[Connector]] = {
    c.name: c
    for c in [
        CfpbComplaintsConnector,
    ]
}


def get_connector(name: str, **params) -> Connector:
    try:
        return REGISTRY[name](**params)
    except KeyError:
        raise ValueError(f"Unknown connector '{name}'. Available: {sorted(REGISTRY)}") from None
