select
    user_id,
    email,
    signup_date,
    country
from {{ ref('raw_users') }}
