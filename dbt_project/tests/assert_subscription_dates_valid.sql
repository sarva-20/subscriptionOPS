-- end_date must never be before start_date
select subscription_id, start_date, end_date
from {{ ref('stg_subscriptions') }}
where end_date is not null and end_date < start_date
