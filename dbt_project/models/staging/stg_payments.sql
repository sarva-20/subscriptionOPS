select
    payment_id,
    subscription_id,
    amount,
    payment_date,
    status
from {{ ref('raw_payments') }}
