with users as (
    select * from {{ ref('stg_users') }}
),

subscriptions as (
    select * from {{ ref('int_subscription_periods') }}
),

subscription_summary as (
    select
        user_id,
        count(*) as total_subscriptions,
        max(is_active) as has_active_subscription,
        max(plan) as latest_plan
    from subscriptions
    group by user_id
)

select
    users.user_id,
    users.email,
    users.signup_date,
    users.country,
    coalesce(subscription_summary.total_subscriptions, 0) as total_subscriptions,
    coalesce(subscription_summary.has_active_subscription, false) as is_active_subscriber,
    subscription_summary.latest_plan
from users
left join subscription_summary
    on users.user_id = subscription_summary.user_id
