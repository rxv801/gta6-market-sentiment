-- One row per ticker per trading day, with the benchmark return for the same date alongside.
-- US tickers use the S&P 500 (^GSPC) as the market; Tokyo-listed 6758.T has no Tokyo benchmark yet, so it gets none.
with returns as (
    select * from {{ ref('int_returns_daily') }}
),

market as (
    select trade_date, daily_return as market_return
    from returns
    where ticker = '^GSPC'
)

select
    returns.return_id as stock_day_id,
    returns.ticker,
    returns.trade_date,
    returns.adj_close_price,
    returns.volume,
    returns.daily_return,
    case when returns.ticker in ('TTWO', 'SONY') then market.market_return end as market_return,
    case when returns.ticker in ('TTWO', 'SONY') then '^GSPC' end as market_ticker,
    returns.ticker in ('^GSPC', '^NDX') as is_benchmark
from returns
left join market
    on returns.trade_date = market.trade_date
