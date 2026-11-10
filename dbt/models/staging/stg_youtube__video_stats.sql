-- One row per video per collector run. YouTube returns counts as strings, so they're cast here.
with source as (
    select * from {{ source('bronze', 'youtube_videos') }}
    where source = 'youtube' and endpoint = 'videos.list'
),

items as (
    select
        source.fetched_at,
        source.run_id,
        item ->> 'id' as video_id,
        item -> 'statistics' as stats
    from source
    cross join lateral jsonb_array_elements(source.payload -> 'items') as item
),

renamed as (
    select
        {{ dbt.hash("video_id || '|' || fetched_at::text") }} as video_stat_id,
        video_id,
        fetched_at,
        (fetched_at at time zone 'UTC')::date as fetched_date_utc,
        run_id,
        (stats ->> 'viewCount')::bigint as view_count,
        (stats ->> 'likeCount')::bigint as like_count,
        (stats ->> 'commentCount')::bigint as comment_count
    from items
),

deduplicated as (
    select
        *,
        row_number() over (partition by video_id, fetched_at order by run_id) as row_num
    from renamed
)

select
    video_stat_id,
    video_id,
    fetched_at,
    fetched_date_utc,
    run_id,
    view_count,
    like_count,
    comment_count
from deduplicated
where row_num = 1
