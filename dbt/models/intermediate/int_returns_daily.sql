-- Simple daily return per ticker from adjusted close: r_t = P_t / P_(t-1) - 1.
-- The previous price is the ticker's previous trading day, so weekends and holidays are skipped,
-- and each exchange keeps its own calendar (6758.T trades on Tokyo days).
with prices as (
    select ticker, trade_date, adj_close_price, volume
    from {{ ref('stg_yfinance__daily_prices') }}
),

with_previous as (
    select
        ticker,
        trade_date,
        adj_close_price,
        volume,
        lag(trade_date) over (partition by ticker order by trade_date) as previous_trade_date,
        lag(adj_close_price) over (partition by ticker order by trade_date) as previous_adj_close_price
    from prices
)

select
    {{ dbt.hash("ticker || '|' || trade_date::text") }} as return_id,
    ticker,
    trade_date,
    previous_trade_date,
    adj_close_price,
    previous_adj_close_price,
    volume,
    adj_close_price / nullif(previous_adj_close_price, 0) - 1 as daily_return
from with_previous
