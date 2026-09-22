{#- Keep only the first 3 ZIP digits (HIPAA Safe Harbor style); anything malformed becomes null. -#}
{% macro mask_zip(column) -%}
    case
        when regexp_matches({{ column }}, '^[0-9]{3}') then left({{ column }}, 3)
    end
{%- endmacro %}

{#- One-way hash for direct identifiers. The salt comes from the environment, never from code. -#}
{% macro hash_pii(column) -%}
    sha256(concat('{{ env_var("PII_SALT", "local-dev-salt") }}', cast({{ column }} as varchar)))
{%- endmacro %}
