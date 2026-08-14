-- a user should not have more than one active subscription at a time
select user_id, count(*) as active_subs
from {{ ref('int_subscription_periods') }}
where is_active = true
group by user_id
having count(*) > 1
