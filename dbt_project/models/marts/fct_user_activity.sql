select
    date_trunc('month', activity_date) as month,
    count(distinct user_id) as monthly_active_users,
    sum(event_count) as total_events,
    avg(event_count) as avg_events_per_active_day
from {{ ref('int_user_activity_daily') }}
group by 1
order by 1
