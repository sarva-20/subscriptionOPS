FROM apache/airflow:3.2.2-python3.12

# Install dbt and its DuckDB adapter, plus faker for data generation,
# into the same Python environment Airflow uses.
RUN pip install --no-cache-dir \
    dbt-duckdb==1.11.0 \
    faker

# Airflow images run as a non-root "airflow" user by default — keep that.
USER airflow
