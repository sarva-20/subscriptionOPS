select month, mrr
from {{ ref('fct_mrr') }}
where mrr < 0
