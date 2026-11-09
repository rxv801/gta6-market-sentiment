{#
    Use the folder's schema (silver, gold) as-is in prod, so tables land in silver.* and gold.*.
    In dev, prefix it with the target schema so local work never mixes with prod names.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- elif target.name == 'prod' -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ target.schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
