# Infrastructure (planned)

Terraform for everything outside the laptop:

- **GCP**
  - GCS raw bucket with one prefix per client
  - One BigQuery dataset per client, with policy tags for PII columns
  - A service account per client, with IAM scoped to its own dataset
  - Cloud Run Job for the Dagster code location
  - Workload Identity Federation for GitHub Actions, so no JSON keys are stored
- **Cloudflare**: D1 database and R2 bucket for dashboard data, the Workers app, and Access
  policies (one per client)

Onboarding a client adds one module call (`module "client_hudson_bank" { ... }`).
