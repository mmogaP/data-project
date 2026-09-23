-- Company benchmark: how each institution handles complaints compared with the market.
-- Companies with fewer than `min_complaints` are excluded to avoid noisy rates.
{% set min_complaints = 50 %}

with by_company as (

    select
        company_name,
        count(*)                                                    as complaints,
        count(distinct product)                                     as products_complained_about,
        avg(case when is_timely_response then 1.0 else 0.0 end)     as timely_response_rate,
        avg(case when is_in_progress then 1.0 else 0.0 end)         as in_progress_rate,
        min(received_date)                                          as first_complaint_date,
        max(received_date)                                          as last_complaint_date
    from {{ ref('fct_complaints') }}
    group by company_name
    having count(*) >= {{ min_complaints }}

)

select
    *,
    round(complaints * 100.0 / sum(complaints) over (), 3)          as market_share_of_complaints_pct,
    rank() over (order by complaints desc)                          as complaint_volume_rank
from by_company
