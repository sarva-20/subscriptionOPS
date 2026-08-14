from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_DIR = "/Users/sarvatarshansankar20/projects/saas-analytics-elt"
DBT_PROJECT_DIR = f"{PROJECT_DIR}/dbt_project"
DBT_VENV_BIN = f"{PROJECT_DIR}/dbt_venv/bin"

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="saas_analytics_elt",
    description="Generate synthetic SaaS data, then seed/run/test the dbt pipeline (DuckDB)",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["dbt", "duckdb", "elt", "saas-analytics"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_DIR} && {DBT_VENV_BIN}/python data_generator/generate_data.py",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_VENV_BIN}/dbt seed",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_VENV_BIN}/dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_VENV_BIN}/dbt test",
    )

    generate_data >> dbt_seed >> dbt_run >> dbt_test
