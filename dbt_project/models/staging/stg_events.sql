select
    event_id,
    user_id,
    event_name,
    event_timestamp
from {{ ref('raw_events') }}
