-- One row per ticker per trading day. Each run re-fetches 10 days, so the same day appears many times in bronze.
-- The most recently fetched row wins, which also picks up later corrections from Yahoo.
with source as (
    select * from {{ source('bronze', 'yfinance_history') }}
    where source = 'yfinance' and endpoint = 'history'
),

bars as (
    select
        source.fetched_at,
        source.payload ->> 'ticker' as ticker,
        bar
    from source
    cross join lateral jsonb_array_elements(source.payload -> 'bars') as bar
),

renamed as (
    select
        ticker,
        (bar ->> 'date')::date as trade_date,
        (bar ->> 'open')::numeric as open_price,
        (bar ->> 'high')::numeric as high_price,
        (bar ->> 'low')::numeric as low_price,
        (bar ->> 'close')::numeric as close_price,
        (bar ->> 'adj_close')::numeric as adj_close_price,
        (bar ->> 'volume')::numeric::bigint as volume,
        fetched_at
    from bars
),

deduplicated as (
    select
        *,
        row_number() over (partition by ticker, trade_date order by fetched_at desc) as row_num
    from renamed
)

select
    {{ dbt.hash("ticker || '|' || trade_date::text") }} as price_id,
    ticker,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    adj_close_price,
    volume,
    fetched_at
from deduplicated
where row_num = 1
