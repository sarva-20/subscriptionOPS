select
    subscription_id,
    user_id,
    plan,
    start_date,
    end_date,
    status,
    case when end_date is null then true else false end as is_active,
    coalesce(
        date_diff('day', start_date, end_date),
        date_diff('day', start_date, current_date)
    ) as duration_days
from {{ ref('stg_subscriptions') }}
