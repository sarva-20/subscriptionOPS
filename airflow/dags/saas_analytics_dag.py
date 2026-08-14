from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Inside the Docker container, these paths are set by the volume mounts
# in docker-compose.yml. No dbt_venv here — dbt is installed directly
# into the container's Python environment via the Dockerfile.
AIRFLOW_HOME = "/opt/airflow"
DBT_PROJECT_DIR = f"{AIRFLOW_HOME}/dbt_project"
DATA_GENERATOR_DIR = f"{AIRFLOW_HOME}/data_generator"

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
        bash_command=f"cd {AIRFLOW_HOME} && python data_generator/generate_data.py",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt seed --profiles-dir .",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test --profiles-dir .",
    )

    generate_data >> dbt_seed >> dbt_run >> dbt_test
