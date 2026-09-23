-- Daily complaint volume by product and state: feeds the trend charts in the dashboard.

select
    received_date,
    product,
    state_code,
    count(*)                                             as complaints,
    count(*) filter (where is_timely_response)           as timely_responses,
    count(*) filter (where is_in_progress)               as in_progress,
    round(avg(days_to_company), 2)                       as avg_days_to_company
from {{ ref('fct_complaints') }}
group by all
