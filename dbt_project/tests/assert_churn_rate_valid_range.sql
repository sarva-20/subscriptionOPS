select month, churn_type, churn_rate_pct
from {{ ref('fct_churn') }}
where churn_rate_pct < 0 or churn_rate_pct > 100
