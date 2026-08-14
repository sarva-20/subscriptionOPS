select
    user_id,
    date_trunc('day', event_timestamp) as activity_date,
    count(*) as event_count,
    count(distinct event_name) as distinct_event_types
from {{ ref('stg_events') }}
group by 1, 2
