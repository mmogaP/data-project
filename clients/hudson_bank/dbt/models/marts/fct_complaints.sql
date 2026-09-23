-- Incremental by partition: each run rebuilds only the days Dagster asks for
-- (vars start_date/end_date, end exclusive). Re-running a day replaces it.
{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='partition_date',
    )
}}

select
    complaint_id,
    received_at,
    received_date,
    sent_to_company_at,
    date_diff('day', received_at, sent_to_company_at) as days_to_company,
    product,
    sub_product,
    issue,
    sub_issue,
    company_name,
    company_response,
    is_timely_response,
    is_in_progress,
    submitted_via,
    state_code,
    zip3,
    tags,
    partition_date,
    _ingested_at
from {{ ref('stg_cfpb__complaints') }}

{% if is_incremental() %}
where partition_date >= cast('{{ var("start_date") }}' as date)
  and partition_date <  cast('{{ var("end_date") }}' as date)
{% endif %}
