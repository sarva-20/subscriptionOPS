"""Read-only dashboard for the SubscriptionOps ELT outputs."""

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("SUBSCRIPTIONOPS_DB", PROJECT_ROOT / "dbt_project" / "dev.duckdb"))
RUN_RESULTS_PATH = PROJECT_ROOT / "dbt_project" / "target" / "run_results.json"

PIPELINE_STEPS = [
    ("01", "Generate data", "Python creates users, subscriptions, events, and payments."),
    ("02", "Load seeds", "dbt loads the generated CSV files into DuckDB."),
    ("03", "Transform models", "Staging and intermediate views feed the analytics marts."),
    ("04", "Run quality checks", "dbt validates keys, relationships, dates, MRR, and churn."),
]


def load_run_results() -> dict[str, Any]:
    if not RUN_RESULTS_PATH.exists():
        return {"results": []}
    with RUN_RESULTS_PATH.open() as file:
        return json.load(file)


def query_database(duckdb: Any, query: str) -> list[tuple[Any, ...]]:
    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        return connection.execute(query).fetchall()


def format_currency(value: Any) -> str:
    return f"${float(value or 0):,.0f}"


def render_table(headers: list[str], rows: list[tuple[Any, ...]]) -> None:
    if not rows:
        st.caption("No rows available.")
        return
    table_rows = [dict(zip(headers, row)) for row in rows]
    st.dataframe(table_rows, width="stretch", hide_index=True)


st.set_page_config(
    page_title="SubscriptionOps Dashboard",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .step-card {
        border: 1px solid #d9e2ec;
        border-radius: 12px;
        padding: 14px;
        min-height: 120px;
        background: #f8fafc;
    }
    .step-number {
        color: #2563eb;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SubscriptionOps")
st.caption("A transparent view of the synthetic SaaS ELT pipeline and its trusted outputs.")

run_results = load_run_results()
results = run_results.get("results", [])
passed = sum(result.get("status") == "pass" for result in results)
failed = sum(result.get("status") == "fail" for result in results)

st.subheader("What happens to the data")
step_columns = st.columns(len(PIPELINE_STEPS))
for column, (number, title, description) in zip(step_columns, PIPELINE_STEPS):
    with column:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-number">{number}</div>
                <strong>{title}</strong>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

if not DB_PATH.exists():
    st.warning(f"DuckDB output not found at `{DB_PATH}`.")
    st.info(
        "Run the pipeline first: `python3 data_generator/generate_data.py`, "
        "then `cd dbt_project && dbt build --profiles-dir .`."
    )
    st.stop()

try:
    import duckdb
except ImportError:
    st.error("DuckDB is not installed. Install dashboard dependencies with `pip install -r dashboard/requirements.txt`.")
    st.stop()

try:
    latest_mrr, latest_activity, latest_churn, active_subscribers = query_database(
        duckdb,
        """
        select
            (select mrr from fct_mrr order by month desc limit 1),
            (select monthly_active_users from fct_user_activity order by month desc limit 1),
            (select coalesce(sum(churned_subscriptions), 0)
             from fct_churn
             where month = (select max(month) from fct_churn)),
            (select count(*) from dim_users where is_active_subscriber)
        """
    )[0]
except duckdb.Error as error:
    st.error(f"Could not read the dbt output: {error}")
    st.info("Run `dbt build --profiles-dir .` from `dbt_project/` and refresh this page.")
    st.stop()

metric_columns = st.columns(5)
metric_columns[0].metric("Latest MRR", format_currency(latest_mrr))
metric_columns[1].metric("Active subscribers", active_subscribers)
metric_columns[2].metric("Monthly active users", latest_activity or 0)
metric_columns[3].metric("Latest churned", latest_churn or 0)
metric_columns[4].metric("dbt tests passed", f"{passed}/{len(results)}")

if failed:
    st.error(f"{failed} dbt test(s) failed in the recorded run.")
elif results:
    st.success("All recorded dbt tests passed.")
else:
    st.warning("No dbt test results were found. Run `dbt test` to populate the pipeline status.")

st.subheader("Latest analytics")
left, right = st.columns(2)
with left:
    st.markdown("#### MRR by month")
    render_table(
        ["month", "active_subscriptions", "mrr"],
        query_database(
            duckdb,
            "select month, active_subscriptions, mrr from fct_mrr order by month desc limit 12"
        ),
    )
with right:
    st.markdown("#### Churn by month")
    render_table(
        ["month", "churn_type", "churned_subscriptions", "churn_rate_pct"],
        query_database(
            duckdb,
            """
            select month, churn_type, churned_subscriptions, churn_rate_pct
            from fct_churn
            order by month desc, churn_type
            limit 12
            """
        ),
    )

st.subheader("Usage and model lineage")
left, right = st.columns(2)
with left:
    st.markdown("#### User activity")
    render_table(
        ["month", "monthly_active_users", "total_events", "avg_events_per_active_day"],
        query_database(
            duckdb,
            """
            select month, monthly_active_users, total_events, avg_events_per_active_day
            from fct_user_activity
            order by month desc
            limit 12
            """
        ),
    )
with right:
    st.markdown("#### dbt model row counts")
    render_table(
        ["model", "rows"],
        query_database(
            duckdb,
            """
            select 'dim_users' as model, count(*) as rows from dim_users
            union all select 'fct_mrr', count(*) from fct_mrr
            union all select 'fct_churn', count(*) from fct_churn
            union all select 'fct_user_activity', count(*) from fct_user_activity
            order by model
            """
        ),
    )

with st.sidebar:
    st.header("Pipeline status")
    st.caption(f"Database: `{DB_PATH}`")
    st.caption(f"Recorded test results: {len(results)}")
    if st.button("Refresh dashboard"):
        st.rerun()
