-- One row per complaint. A complaint's status changes after it is first published
-- (e.g. "In progress" -> "Closed with explanation"), so re-ingesting a day can bring a
-- newer version of the same complaint_id. Keep the most recently ingested one.

with source as (

    select * from {{ source('raw', 'cfpb_complaints') }}

),

deduplicated as (

    select *
    from source
    qualify row_number() over (partition by complaint_id order by _ingested_at desc) = 1

)

select
    cast(complaint_id as bigint)                     as complaint_id,
    cast(date_received as timestamp)                 as received_at,
    cast(cast(date_received as timestamp) as date)   as received_date,
    cast(date_sent_to_company as timestamp)          as sent_to_company_at,
    product,
    sub_product,
    issue,
    sub_issue,
    company                                          as company_name,
    company_response,
    company_public_response,
    timely = 'Yes'                                   as is_timely_response,
    company_response = 'In progress'                 as is_in_progress,
    submitted_via,
    upper(state)                                     as state_code,
    {{ dbt_core.mask_zip('zip_code') }}              as zip3,
    tags,
    cast(ds as date)                                 as partition_date,
    _ingested_at
from deduplicated
