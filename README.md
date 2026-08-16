<div align=*center*>

# 📊 SaaS Analytics ELT Pipeline

*An end-to-end, open-source data pipeline simulating the analytics backbone of a SaaS company — transforming raw event logs into high-impact **MRR** and churn metrics.*

[![Python](https://img.shields.io/badge/Python-3.10+-**3776AB**?style=for-the-badge&logo=python&logoColor=white)](https://[www.python.org/](https://www.python.org/)) [![dbt](https://img.shields.io/badge/dbt-Core-**FF694B**?style=for-the-badge&logo=dbt&logoColor=white)](https://[www.getdbt.com/](https://www.getdbt.com/)) [![DuckDB](https://img.shields.io/badge/DuckDB-Latest-**FFF000**?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/) [![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-2.x-**017CEE**?style=for-the-badge&logo=apacheairflow&logoColor=white)](https://airflow.apache.org/) [![Docker](https://img.shields.io/badge/Docker-Containerized-**2496ED**?style=for-the-badge&logo=docker&logoColor=white)](https://[www.docker.com/](https://www.docker.com/)) [![CI](https://img.shields.io/badge/GitHub_Actions-Automated_Testing-**2088FF**?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

</div>

---

## 📌 Executive Summary

This project simulates a production-grade data pipeline for a SaaS product. It dynamically generates realistic user, subscription, and billing data, cleans and transforms raw logs, and builds executive-ready data marts to track **Active Users**, **Monthly Recurring Revenue (**MRR**)**, and **Churn**.

> [!**NOTE**] > **Key Highlight — Granular Churn Attribution** > Standard metrics lump all customer losses together. This pipeline automatically isolates **Voluntary Churn** (customer choice) from **Involuntary Churn** (failed payment retries). Voluntary churn requires product/retention updates; involuntary churn requires payment retry optimization.

---

## 🏗️ Pipeline Architecture

The data flows cleanly through modular layer transformations, where each layer strictly depends on the previous stage.

┌─────────────────┐       ┌─────────────────┐       ┌──────────────────────┐       ┌─────────────────┐│  Raw **CSV** Seeds  │ ────> │ Staging Models  │ ────> │ Intermediate Logic   │ ────> │   Data Marts    ││ (Fake Data Gen) │       │ (Light Cleanup) │       │ (Subscription State) │       │ (Final Analytics)│└─────────────────┘       └─────────────────┘       └──────────────────────┘       └─────────────────┘
| Layer | Responsibility | Key Output Tables |
| :--- | :--- | :--- |
| **Raw Seeds** | Python (`faker`) generated transactional data | `raw_users`, `raw_subscriptions`, `raw_payments` |
| **Staging** | Renaming columns, casting types, zero business logic | `stg_users`, `stg_subscriptions`, `stg_payments` |
| **Intermediate**| Calculation of active periods & billing windows | `int_subscription_periods`, `int_payment_failures` |
| **Marts** | Final aggregated analytics tables for querying | `dim_users`, `fct_mrr`, `fct_user_activity`, `fct_churn` |

---

## ⚙️ How It Works

### 🎲 Real-World Synthetic Data Generation

`data_generator/generate_data.py` uses `faker` to build **~**500** fake users** spanning **18 months** with realistic behaviors:
- Tiered plans: *Free*, *Pro*, and *Enterprise*.
- ~30% overall churn rate.
- **Pre-churn activity drop**: Engagement gradually fades in the weeks leading up to cancellation, mimicking real customer behavior.
- Real-world payment processing errors (failed credit cards/retries).

### 💡 Voluntary vs. Involuntary Churn Logic

```math \text{Monthly Churn Rate} = \frac{\text{Subscriptions Churned in Month}}{\text{Active Subscriptions at Start of Month}} When a subscription terminates, the model evaluates payment logs:Involuntary Churn: At least one payment failed in the 60 days prior to termination. (Billing infrastructure failure).Voluntary Churn: No payment failures prior to termination. (Customer proactively canceled).🚀 Quickstart GuideOption 1: Docker (Recommended — One Command)Run the full stack containerized with Airflow and dbt pre-configured:Bashdocker compose up --build Accessing the Airflow Orchestration Interface:Retrieve the auto-generated credentials:Bashdocker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated Open [http://localhost:**8080**](http://localhost:**8080**) in your browser.Log in with username admin and the generated password.Unpause and trigger the saas_analytics_elt **DAG**.Option 2: Local Execution (dbt **CLI** + Python)If you prefer to run the data transformations directly without Docker or Airflow:Bash# 1. Setup virtual environment & dependencies python -m venv venv source venv/bin/activate  # On Windows: venv\Scripts\activate pip install dbt-duckdb faker

# 2. Generate raw synthetic datasets

python data_generator/generate_data.py

# 3. Execute dbt seeds, transformations, and assertions

cd dbt_project dbt seed dbt run dbt test

# 4. Preview final metrics

dbt show --select fct_churn --limit 20 🧪 Data Quality & Automated TestingThe project includes 26+ automated dbt tests running on every build and CI push:Generic Integrity Tests: Primary key uniqueness, non-null checks, foreign key referential integrity.Custom Business Rule Assertions:Subscription end date must be $\ge$ start date.**MRR** values can never fall below zero.Users cannot hold multiple overlapping active subscriptions.Calculated monthly churn rates must fall strictly between 0% and **100**%.📂 Project StructurePlaintextsaas-analytics-elt/ ├── data_generator/         # Python script creating realistic synthetic data ├── dbt_project/            # Complete dbt transformation setup │   ├── seeds/              # Target directory for generated raw CSVs │   ├── models/ │   │   ├── staging/        # 1:1 cleanup & standardization of raw tables │   │   ├── intermediate/   # Complex business logic & active window modeling │   │   └── marts/          # Final reporting tables (dim_users, fct_mrr, fct_churn, etc.) │   └── tests/              # Custom **SQL** assertions enforcing business rules ├── airflow/dags/           # **DAG** definition orchestrating seed -> run -> test ├── Dockerfile              # Unified container definition (Airflow + dbt) ├── docker-compose.yml      # Multi-container orchestration setup └── .github/workflows/ci.yml # Automated CI pipeline triggered on GitHub push

---

Review the updated **README** formatting. Does the structure, visual hierarchy, or badges need any adjustments, or would you like to add/modify any sections?
