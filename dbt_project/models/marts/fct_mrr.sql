with months as (
    select unnest(generate_series(
        date_trunc('month', (select min(start_date) from {{ ref('int_subscription_periods') }})),
        date_trunc('month', current_date),
        interval '1 month'
    )) as month
),

subscriptions as (
    select * from {{ ref('int_subscription_periods') }}
),

plan_prices as (
    select 'free' as plan, 0 as price
    union all select 'pro', 29
    union all select 'enterprise', 199
)

select
    months.month,
    count(distinct subscriptions.subscription_id) as active_subscriptions,
    sum(plan_prices.price) as mrr
from months
left join subscriptions
    on months.month >= date_trunc('month', subscriptions.start_date)
    and (subscriptions.end_date is null or months.month < date_trunc('month', subscriptions.end_date))
left join plan_prices
    on subscriptions.plan = plan_prices.plan
group by months.month
order by months.month
