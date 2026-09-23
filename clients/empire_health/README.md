# Empire Health Network (planned)

Fictional healthcare client. It shows that the platform onboards a second industry by adding
config, connectors and a dbt project, without changing orchestration code.

Planned sources:

- **Synthea**: synthetic patient records in FHIR format (encounters, conditions, medications).
- **openFDA**: drug adverse event reports (`/drug/event.json`, public API).
- **NY SPARCS**: New York hospital inpatient discharges and costs (health.data.ny.gov).

Planned marts: 30-day readmission rate, cohorts by condition, adverse events per medication.
Patient identifiers are hashed in staging with `dbt_core.hash_pii`, and only 3-digit ZIPs are kept.

To enable it: add connectors to `src/dataplatform/connectors`, list the sources in `client.yml`,
create `dbt/`, then set `enabled: true`.
