with subscriptions as (
    select * from {{ ref('int_subscription_periods') }}
    where status = 'canceled'
),

payments as (
    select * from {{ ref('stg_payments') }}
),

failed_payment_counts as (
    select
        subscriptions.subscription_id,
        count(*) filter (
            where payments.status = 'failed'
            and payments.payment_date between subscriptions.end_date - interval '60 days' and subscriptions.end_date
        ) as failed_payments_before_churn
    from subscriptions
    left join payments
        on subscriptions.subscription_id = payments.subscription_id
    group by subscriptions.subscription_id
),

churn_events as (
    select
        subscriptions.subscription_id,
        subscriptions.user_id,
        subscriptions.plan,
        subscriptions.end_date as churn_date,
        date_trunc('month', subscriptions.end_date) as churn_month,
        subscriptions.duration_days,
        case
            when coalesce(failed_payment_counts.failed_payments_before_churn, 0) >= 1
                then 'involuntary'
            else 'voluntary'
        end as churn_type
    from subscriptions
    left join failed_payment_counts
        on subscriptions.subscription_id = failed_payment_counts.subscription_id
),

active_at_month_start as (
    select
        date_trunc('month', months.month) as month,
        count(distinct all_subs.subscription_id) as active_subscriptions_start_of_month
    from (
        select unnest(generate_series(
            date_trunc('month', (select min(start_date) from {{ ref('int_subscription_periods') }})),
            date_trunc('month', current_date),
            interval '1 month'
        )) as month
    ) as months
    left join {{ ref('int_subscription_periods') }} as all_subs
        on months.month >= date_trunc('month', all_subs.start_date)
        and (all_subs.end_date is null or months.month < date_trunc('month', all_subs.end_date))
    group by months.month
)

select
    churn_events.churn_month as month,
    churn_events.churn_type,
    count(*) as churned_subscriptions,
    active_at_month_start.active_subscriptions_start_of_month,
    round(
        count(*) * 100.0 / nullif(active_at_month_start.active_subscriptions_start_of_month, 0),
        2
    ) as churn_rate_pct
from churn_events
left join active_at_month_start
    on churn_events.churn_month = active_at_month_start.month
group by 1, 2, 4
order by 1, 2
