-- One row per poll: total viewers and live streams in the GTA VI category. Empty until #21 re-enables the poller.
with source as (
    select * from {{ source('bronze', 'twitch_streams') }}
    where source = 'twitch' and endpoint = 'streams'
),

renamed as (
    select
        fetched_at,
        run_id,
        payload ->> 'game_id' as game_id,
        payload ->> 'game_name' as game_name,
        (payload ->> 'viewer_count')::integer as viewer_count,
        (payload ->> 'stream_count')::integer as stream_count,
        (payload ->> 'truncated')::boolean as is_truncated
    from source
),

deduplicated as (
    select
        *,
        row_number() over (partition by game_id, fetched_at order by run_id) as row_num
    from renamed
)

select
    {{ dbt.hash("game_id || '|' || fetched_at::text") }} as category_total_id,
    fetched_at,
    run_id,
    game_id,
    game_name,
    viewer_count,
    stream_count,
    is_truncated
from deduplicated
where row_num = 1
