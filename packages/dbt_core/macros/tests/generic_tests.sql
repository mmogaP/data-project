{% test not_negative(model, column_name) %}
    select * from {{ model }} where {{ column_name }} < 0
{% endtest %}

{% test between(model, column_name, min_value, max_value) %}
    select * from {{ model }}
    where {{ column_name }} < {{ min_value }} or {{ column_name }} > {{ max_value }}
{% endtest %}

{#- Fails when the newest row is older than max_days_old: catches silently stalled pipelines. -#}
{% test recent_data(model, date_column, max_days_old) %}
    select max({{ date_column }}) as latest
    from {{ model }}
    having max({{ date_column }}) is null
        or max({{ date_column }}) < current_date - interval '{{ max_days_old }} days'
{% endtest %}
