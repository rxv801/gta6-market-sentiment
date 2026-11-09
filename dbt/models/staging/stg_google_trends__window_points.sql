-- One row per term, window and day. Windows stay separate here because each is scaled to its own peak;
-- they are stitched into one series downstream (see docs/methods/google-trends.md).
-- If the same window was fetched twice, the latest fetch wins.
with source as (
    select * from {{ source('bronze', 'google_trends') }}
    where source = 'google_trends' and endpoint = 'interest_over_time'
),

points as (
    select
        source.fetched_at,
        source.payload ->> 'term' as search_term,
        source.payload ->> 'geo' as geo,
        (source.payload ->> 'start')::date as window_start,
        (source.payload ->> 'end')::date as window_end,
        point
    from source
    cross join lateral jsonb_array_elements(source.payload -> 'points') as point
),

renamed as (
    select
        search_term,
        geo,
        window_start,
        window_end,
        (point ->> 'date')::date as interest_date,
        (point ->> 'value')::integer as interest_value,
        (point ->> 'is_partial')::boolean as is_partial,
        fetched_at
    from points
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by search_term, geo, window_start, window_end, interest_date
            order by fetched_at desc
        ) as row_num
    from renamed
)

select
    {{ dbt.hash("search_term || '|' || geo || '|' || window_start::text || '|' || window_end::text || '|' || interest_date::text") }}
        as window_point_id,
    search_term,
    geo,
    window_start,
    window_end,
    interest_date,
    interest_value,
    is_partial,
    fetched_at
from deduplicated
where row_num = 1
