# 📊 SubscriptionOps

A production-style ELT project that simulates the analytics backbone of a SaaS business — from synthetic customer and billing events to trusted executive metrics like MRR, active users, and churn.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Latest-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Airflow](https://img.shields.io/badge/Apache_Airflow-2.x-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/GitHub_Actions-Automated_Testing-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

## Overview

This repository models a realistic SaaS analytics platform using synthetic data, dbt transformations, and Airflow orchestration. It is designed to showcase how raw operational signals can be transformed into product and finance metrics that support retention, growth, and customer health analysis.

The pipeline generates realistic customer, subscription, payment, and usage behavior across a multi-month time horizon, then transforms that data into reusable analytics tables and business logic for analysis.

## Why this project

Modern SaaS teams need dependable operational metrics that distinguish between:

- product-driven retention signals,
- billing-related churn,
- active customer health,
- and recurring revenue performance.

This project focuses on those patterns in a clean, modular, and easy-to-understand architecture.

## Core capabilities

- Synthetic SaaS dataset generation using Python and Faker
- dbt-based staging, intermediate, and mart layers
- Coverage for active users, MRR, churn, and customer lifecycle logic
- Clear separation between voluntary and involuntary churn
- Orchestration via Apache Airflow
- Dockerized local execution for rapid onboarding
- Automated dbt quality checks and CI validation

## Business logic

### Retention and churn modeling

The project distinguishes between two primary churn categories:

- Voluntary churn: a customer cancels intentionally
- Involuntary churn: cancellation follows failed payment or billing friction

This allows teams to isolate product/retention issues from payment and billing problems, which is often a critical gap in basic revenue reporting.

### Example metric logic

Monthly churn rate can be expressed as:

$$
\text{Monthly Churn Rate} = \frac{\text{Subscriptions churned in month}}{\text{Active subscriptions at start of month}}
$$

The model evaluates payment signals near the point of cancellation, enabling a more accurate interpretation of customer loss and retention risk.

## Architecture

The pipeline follows a layered ELT structure:

```text
Raw CSV Seeds
    ↓
Staging Models
    ↓
Intermediate Logic
    ↓
Analytics Marts
```

| Layer | Responsibility | Example outputs |
| --- | --- | --- |
| Raw Seeds | Synthetic operational data generation | `raw_users`, `raw_subscriptions`, `raw_payments` |
| Staging | Standardize and clean inbound data | `stg_users`, `stg_subscriptions`, `stg_payments` |
| Intermediate | Subscription windows, billing activity, and churn attribution | `int_subscription_periods`, `int_payment_failures` |
| Marts | Business-ready analytics tables | `dim_users`, `fct_mrr`, `fct_user_activity`, `fct_churn` |

## What the pipeline produces

The project is built to answer common SaaS revenue and retention questions such as:

- How much recurring revenue is active each month?
- Which customers are still engaged?
- Which churn events were voluntary vs. involuntary?
- Which customers are slipping before cancellation?
- Are payment failures driving churn behavior?

## Data generation

The synthetic data generator creates realistic SaaS events across a multi-month time horizon, including:

- Free, Pro, and Enterprise plan tiers
- User lifecycle segmentation
- Subscription start and end events
- Payment retries and billing friction
- Pre-churn activity declines
- Subscription cancellations with realistic context

## Project structure

```text
saas-analytics-elt/
├── data_generator/
│   └── generate_data.py              # Generates realistic SaaS datasets
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── seeds/
│   ├── tests/
│   └── dbt_project.yml
├── airflow/
│   └── dags/
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
├── requirements.txt
├── README.md
└── LICENSE
```

## Quick start

### Option 1: Docker (recommended)

Run the full stack with Airflow and dbt configured in a single workflow:

```bash
docker compose up --build
```

Then open the Airflow UI at:

```text
http://localhost:8080
```

Retrieve the generated admin credentials:

```bash
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
```

Log in with the generated username and password, then unpause and trigger the DAG.

### Option 2: Local execution

If you prefer to run the transformation layer directly:

```bash
python -m venv venv
source venv/bin/activate
pip install dbt-duckdb faker

python data_generator/generate_data.py

cd dbt_project
dbt seed
dbt run
dbt test

dbt show --select fct_churn --limit 20
```

## Data quality and testing

This project includes business-rule and integrity checks for reliable outputs, including:

- primary key uniqueness
- null validation
- referential integrity checks
- subscription validity checks
- non-negative MRR validation
- no overlapping active subscriptions
- churn-rate range validation between 0% and 100%

These checks ensure the final data models remain trustworthy for reporting and analysis.

## Tech stack

- Python
- dbt Core
- DuckDB
- Apache Airflow
- Docker
- GitHub Actions

## Roadmap

Planned enhancements include:

- richer product usage cohorts
- executive dashboard exports
- more advanced retention segmentation
- additional warehouse compatibility
- optional BI visualization layer

## License

This project is licensed under the MIT License. See the license file for details.

## Contributing

Contributions are welcome. If you want to improve the data model, expand the synthetic data realism, or strengthen the test coverage, open a pull request with a clear summary of the change.

## Contact

For project discussions, suggestions, or collaboration opportunities, open an issue or start a discussion in the repository.
