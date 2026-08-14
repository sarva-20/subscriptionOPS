"""
Synthetic SaaS data generator for the analytics ELT pipeline.
Produces users, subscriptions, events, and payments CSVs with
realistic churn patterns for meaningful downstream analysis.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

OUTPUT_DIR = Path(__file__).parent.parent / "dbt_project" / "seeds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NUM_USERS = 500
START_DATE = datetime(2024, 3, 1)
END_DATE = datetime(2026, 8, 1)
PLANS = {"free": 0, "pro": 29, "enterprise": 199}
PLAN_WEIGHTS = [0.5, 0.35, 0.15]
COUNTRIES = ["US", "IN", "UK", "DE", "CA", "AU", "SG"]

users = []
subscriptions = []
events = []
payments = []

user_id_counter = 1
sub_id_counter = 1
event_id_counter = 1
payment_id_counter = 1


def random_date_between(start, end):
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))


for _ in range(NUM_USERS):
    user_id = user_id_counter
    user_id_counter += 1

    signup_date = random_date_between(START_DATE, END_DATE - timedelta(days=30))
    country = random.choice(COUNTRIES)

    users.append({
        "user_id": user_id,
        "email": fake.unique.email(),
        "signup_date": signup_date.strftime("%Y-%m-%d"),
        "country": country,
    })

    # Subscription: does this user churn?
    will_churn = random.random() < 0.30
    plan = random.choices(list(PLANS.keys()), weights=PLAN_WEIGHTS)[0]

    sub_start = signup_date
    if will_churn:
        # subscription lasts 1-12 months then ends
        duration_days = random.randint(30, 365)
        sub_end = min(sub_start + timedelta(days=duration_days), END_DATE)
        status = "canceled"
    else:
        sub_end = None
        status = "active"

    sub_id = sub_id_counter
    sub_id_counter += 1

    subscriptions.append({
        "subscription_id": sub_id,
        "user_id": user_id,
        "plan": plan,
        "start_date": sub_start.strftime("%Y-%m-%d"),
        "end_date": sub_end.strftime("%Y-%m-%d") if sub_end else "",
        "status": status,
    })

    # Payments: monthly, for the active duration of the subscription
    if plan != "free":
        payment_date = sub_start
        end_bound = sub_end if sub_end else END_DATE
        while payment_date < end_bound:
            payment_status = "failed" if random.random() < 0.05 else "success"
            payments.append({
                "payment_id": payment_id_counter,
                "subscription_id": sub_id,
                "amount": PLANS[plan],
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "status": payment_status,
            })
            payment_id_counter += 1
            payment_date += timedelta(days=30)

    # Events: daily-ish activity, with decay before churn
    event_names = ["login", "feature_used", "report_viewed", "invite_sent", "settings_updated"]
    activity_end = sub_end if sub_end else END_DATE
    day = sub_start
    while day < activity_end:
        days_until_end = (activity_end - day).days

        # decay activity probability in the last 30 days before churn
        if will_churn and days_until_end < 30:
            activity_prob = 0.6 * (days_until_end / 30)
        else:
            activity_prob = 0.6

        if random.random() < activity_prob:
            num_events_today = random.randint(1, 4)
            for _ in range(num_events_today):
                events.append({
                    "event_id": event_id_counter,
                    "user_id": user_id,
                    "event_name": random.choice(event_names),
                    "event_timestamp": day.strftime("%Y-%m-%d %H:%M:%S"),
                })
                event_id_counter += 1

        day += timedelta(days=1)


def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


write_csv("raw_users.csv", users, ["user_id", "email", "signup_date", "country"])
write_csv("raw_subscriptions.csv", subscriptions, ["subscription_id", "user_id", "plan", "start_date", "end_date", "status"])
write_csv("raw_events.csv", events, ["event_id", "user_id", "event_name", "event_timestamp"])
write_csv("raw_payments.csv", payments, ["payment_id", "subscription_id", "amount", "payment_date", "status"])
