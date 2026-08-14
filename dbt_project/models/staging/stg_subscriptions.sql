select
    subscription_id,
    user_id,
    plan,
    start_date,
    end_date,
    status
from {{ ref('raw_subscriptions') }}
