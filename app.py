# dataset.py
import os, random
from collections import Counter
import pandas as pd

SEED = 42
rng = random.Random(SEED)
CSV_PATH = os.path.join(os.path.dirname(__file__), "Banking.csv")

CATEGORIES = ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"]
STATUSES = ["Submitted", "Under Review", "Approved", "Rejected", "Disbursed"]
STATUS_WEIGHTS = [0.10, 0.15, 0.20, 0.10, 0.45]

CATEGORY_MAP = {
    "Personal Loan": "Personal Loan",
    "Home Loan": "Home Loan",
    "Car Loan": "Auto Loan",
    "Education Loan": "Education Loan",
    "Business Loan": "Business Loan"
}

df = pd.read_csv(CSV_PATH)

REQUIRED_COLUMNS = [
    "Lender_Type", "Customer_ID", "Loan_ID", "Loan_Type", "Loan_Purpose",
    "Loan_Amount", "Interest_Rate", "Loan_Term_Months", "Repayment_Status",
    "NPA_Status", "Pending_Amount", "Non_Repayment_EMIs", "Recovery_Status",
    "Prepayment_Option", "EMI_Amount", "Credit_Score", "Account_Type",
    "Customer_Segment"
]

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")


def fraud_flag(row):
    risk = (
        2 * (str(row["NPA_Status"]) == "Yes")
        + (int(row["Non_Repayment_EMIs"]) >= 4)
        + (float(row["Pending_Amount"]) > 0)
        + (int(row["Credit_Score"]) < 650)
    )
    p = 0.35 if risk >= 4 else 0.20 if risk >= 2 else 0.10
    return rng.random() < p


LOAN_APPLICATIONS = []

for i, row in df.iterrows():
    category = CATEGORY_MAP.get(row["Loan_Type"])
    if not category:
        continue

    LOAN_APPLICATIONS.append({
        "record_id": f"REC{i + 1:04d}",
        "source_loan_id": str(row["Loan_ID"]),
        "category": category,
        "status": rng.choices(STATUSES, STATUS_WEIGHTS, k=1)[0],
        "loan_amount_inr": int(row["Loan_Amount"]),
        "days_since_created": rng.randint(0, 30),
        "flagged_for_fraud_review": fraud_flag(row),
        "customer_id": str(row["Customer_ID"]),
        "lender_type": str(row["Lender_Type"]),
        "loan_purpose": str(row["Loan_Purpose"]),
        "interest_rate": float(row["Interest_Rate"]),
        "loan_term_months": int(row["Loan_Term_Months"]),
        "repayment_status": str(row["Repayment_Status"]),
        "npa_status": str(row["NPA_Status"]),
        "pending_amount": float(row["Pending_Amount"]),
        "non_repayment_emis": int(row["Non_Repayment_EMIs"]),
        "recovery_status": str(row["Recovery_Status"]),
        "prepayment_option": str(row["Prepayment_Option"]),
        "emi_amount": float(row["EMI_Amount"]),
        "credit_score": int(row["Credit_Score"]),
        "account_type": str(row["Account_Type"]),
        "customer_segment": str(row["Customer_Segment"])
    })

LOAN_APPLICATION_INDEX = {x["record_id"]: x for x in LOAN_APPLICATIONS}


def get_loan_application(record_id):
    return LOAN_APPLICATION_INDEX.get(str(record_id))


def validate_dataset():
    n = len(LOAN_APPLICATIONS)
    cats = Counter(x["category"] for x in LOAN_APPLICATIONS)
    stats = Counter(x["status"] for x in LOAN_APPLICATIONS)
    fraud = sum(x["flagged_for_fraud_review"] for x in LOAN_APPLICATIONS)
    amounts = [x["loan_amount_inr"] for x in LOAN_APPLICATIONS]
    ids = [x["record_id"] for x in LOAN_APPLICATIONS]

    assert n >= 40
    assert all(cats[c] >= 3 for c in CATEGORIES)
    assert all(stats[s] >= 1 for s in STATUSES)
    assert 10 <= fraud / n * 100 <= 30
    assert all(0 <= x["days_since_created"] <= 30 for x in LOAN_APPLICATIONS)
    assert len(ids) == len(set(ids))

    print("=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)
    print(f"Seed: {SEED} | Records: {n}")
    print("Categories:", dict(cats))
    print("Statuses:", dict(stats))
    print(f"Status weights: {dict(zip(STATUSES, STATUS_WEIGHTS))}")
    print(f"Fraud review: {fraud}/{n} ({fraud/n*100:.2f}%)")
    print(f"Loan range: INR {min(amounts):,} - INR {max(amounts):,}")
    print(f"Unique IDs: {len(set(ids))}/{n}")
    print("VALIDATION PASSED")


if __name__ == "__main__":
    validate_dataset()
    print("\nSample:", LOAN_APPLICATIONS[:3])
