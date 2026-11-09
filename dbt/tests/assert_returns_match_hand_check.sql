-- Hand check (WH-5): TTWO daily returns worked out by hand from Yahoo closes on three event dates.
-- TTWO pays no dividend, so adjusted close equals close on these dates.
--   2023-12-05 (Trailer 1, e04):   156.76 / 157.56 - 1 = -0.005077
--   2024-05-17 (fall 2025, e05):   147.84 / 146.08 - 1 =  0.012048
--   2025-05-02 (first delay, e06): 219.50 / 235.17 - 1 = -0.066633
-- Fails if a computed return is more than 0.0001 away, or if a date is missing while TTWO data covers it.
with hand_check (ticker, trade_date, expected_return) as (
    values
        ('TTWO', date '2023-12-05', -0.005077),
        ('TTWO', date '2024-05-17', 0.012048),
        ('TTWO', date '2025-05-02', -0.066633)
),

coverage as (
    select min(trade_date) as first_day, max(trade_date) as last_day
    from {{ ref('int_returns_daily') }}
    where ticker = 'TTWO'
)

select
    hand_check.ticker,
    hand_check.trade_date,
    hand_check.expected_return,
    returns.daily_return
from hand_check
cross join coverage
left join {{ ref('int_returns_daily') }} as returns
    on returns.ticker = hand_check.ticker
    and returns.trade_date = hand_check.trade_date
where hand_check.trade_date > coverage.first_day
  and hand_check.trade_date <= coverage.last_day
  and (returns.daily_return is null or abs(returns.daily_return - hand_check.expected_return) > 0.0001)
