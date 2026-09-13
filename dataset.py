import csv
import json
import os
import random

from datetime import datetime, timedelta
from typing import Dict, List

SEED = 42
RECORD_COUNT = 1000

OUTPUT_DIR = "data"

JSON_OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "loan_applications.json"
)

CSV_OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "generated_loan_applications.csv"
)

lender_types = [
    "Bank",
    "NBFC",
    "P2P Lending"
]

lender_weights = [
    50,
    25,
    25
]


loan_types = [
    "Personal Loan",
    "Home Loan",
    "Auto Loan",
    "Business Loan",
    "Education Loan"
]


loan_purposes = {

    "Personal Loan": [
        "Medical Expenses",
        "Wedding Expenses",
        "Debt Consolidation"
    ],

    "Home Loan": [
        "Residential Property",
        "Renovation"
    ],

    "Auto Loan": [
        "Vehicle Purchase"
    ],

    "Business Loan": [
        "Working Capital",
        "Business Expansion",
        "Startup Funding"
    ],

    "Education Loan": [
        "Higher Education",
        "Overseas Study"
    ]
}


repayment_statuses = [
    "Submitted",
    "Under Review",
    "Approved",
    "Rejected",
    "Disbursed"
]


status_weights = [
    20,
    25,
    30,
    15,
    10
]


branch_locations = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Pune",
    "Gurugram",
    "Jaipur",
    "Ahmedabad",
    "Lucknow",
    "Patna"
]


first_names = [
    "Rahul",
    "Anita",
    "Kunal",
    "Neha",
    "Amit",
    "Pooja",
    "Arjun",
    "Meera",
    "Vikram",
    "Shalini",
    "Rajesh",
    "Sneha",
    "Deepak",
    "Shreya",
    "Rohit",
    "Megha",
    "Suresh",
    "Sunita",
    "Anjali"
]


last_names = [
    "Sharma",
    "Verma",
    "Mehta",
    "Kapoor",
    "Singh",
    "Nair",
    "Patel",
    "Joshi",
    "Rao",
    "Gupta",
    "Kumar",
    "Iyer",
    "Malhotra",
    "Desai",
    "Rathi",
    "Bansal"
]

def random_date(
    start_year: int = 2019,
    end_year: int = 2025
) -> datetime:

    start = datetime(
        start_year,
        1,
        1
    )

    end = datetime(
        end_year,
        12,
        31
    )

    total_days = (
        end - start
    ).days

    return start + timedelta(
        days=random.randint(
            0,
            total_days
        )
    )


def generate_customer_name() -> str:

    first_name = random.choice(
        first_names
    )

    last_name = random.choice(
        last_names
    )

    return (
        f"{first_name} {last_name}"
    )

def generate_loan_dataset(
    seed: int = SEED,
    count: int = RECORD_COUNT
) -> List[Dict]:

    """
    Generate deterministic synthetic loan-application records.

    Required capstone fields:
        record_id
        category
        status
        loan_amount_inr
        days_since_created
        flagged_for_fraud_review
    """

    random.seed(
        seed
    )

    records = []


    for i in range(
        count
    ):


        record_id = (
            f"CRD-LN-{1001 + i}"
        )

        customer_id = (
            f"CUST-{10001 + i}"
        )


        lender = random.choices(
            lender_types,
            weights=lender_weights,
            k=1
        )[0]


        category = random.choice(
            loan_types
        )

        loan_purpose = random.choice(
            loan_purposes[
                category
            ]
        )



        loan_amount = (
            random.randint(
                200,
                5000
            )
            *
            1000
        )


        interest_rate = round(
            random.uniform(
                7.0,
                15.0
            ),
            1
        )


        term_months = random.choice(
            [
                24,
                36,
                48,
                60,
                96,
                120,
                180,
                240
            ]
        )


        start_datetime = (
            random_date()
        )


        start_date = (
            start_datetime.strftime(
                "%Y-%m-%d"
            )
        )


        end_datetime = (

            start_datetime

            +

            timedelta(
                days=term_months * 30
            )
        )


        end_date = (
            end_datetime.strftime(
                "%Y-%m-%d"
            )
        )


        status = random.choices(
            repayment_statuses,
            weights=status_weights,
            k=1
        )[0]


        # Required field
        days_since_created = (
            random.randint(
                0,
                30
            )
        )



        flagged_for_fraud = (
            random.random()
            <
            0.18
        )



        if status in [
            "Rejected",
            "Disbursed"
        ]:

            pending_amount = 0

        else:

            pending_amount = (
                loan_amount
            )


        if status == "Under Review":

            non_repayment_emis = (
                random.randint(
                    0,
                    6
                )
            )

        else:

            non_repayment_emis = 0


        if status == "Rejected":

            default_date = (
                random_date(
                    2024,
                    2026
                )
                .strftime(
                    "%Y-%m-%d"
                )
            )

        else:

            default_date = ""


        if status == "Rejected":

            recovery_status = (
                "Recovery"
            )

        elif status in [
            "Approved",
            "Disbursed"
        ]:

            recovery_status = (
                "Active"
            )

        else:

            recovery_status = (
                "Pending"
            )


        if category == "Home Loan":

            collateral = "House"

        elif category == "Auto Loan":

            collateral = "Car"

        elif category == "Business Loan":

            collateral = "Factory"

        else:

            collateral = "None"


        guarantor = random.choice(
            [
                "None",
                "Father",
                "Mother",
                "Brother",
                "Husband",
                "Wife"
            ]
        )


        prepayment_option = (
            random.choice(
                [
                    "Yes",
                    "No"
                ]
            )
        )


        # Simple synthetic value.
        # This is not a financial EMI formula.
        emi_amount = round(
            loan_amount
            /
            term_months,
            0
        )



        customer_name = (
            generate_customer_name()
        )


        age = random.randint(
            21,
            60
        )


        gender = random.choice(
            [
                "M",
                "F"
            ]
        )


        account_type = random.choice(
            [
                "Savings",
                "Current"
            ]
        )


        credit_score = random.randint(
            600,
            800
        )


        customer_segment = (
            random.choice(
                [
                    "Retail",
                    "SME",
                    "Corporate"
                ]
            )
        )


        branch_location = (
            random.choice(
                branch_locations
            )
        )


        record = {

            # Required capstone fields
            "record_id":
                record_id,

            "category":
                category,

            "status":
                status,

            "loan_amount_inr":
                loan_amount,

            "days_since_created":
                days_since_created,

            "flagged_for_fraud_review":
                flagged_for_fraud,


            # Additional fields
            "lender_type":
                lender,

            "customer_id":
                customer_id,

            "loan_purpose":
                loan_purpose,

            "interest_rate":
                interest_rate,

            "term_months":
                term_months,

            "start_date":
                start_date,

            "end_date":
                end_date,

            "pending_amount":
                pending_amount,

            "non_repayment_emis":
                non_repayment_emis,

            "default_date":
                default_date,

            "recovery_status":
                recovery_status,

            "collateral":
                collateral,

            "guarantor":
                guarantor,

            "prepayment_option":
                prepayment_option,

            "emi_amount":
                emi_amount,

            "customer_name":
                customer_name,

            "age":
                age,

            "gender":
                gender,

            "account_type":
                account_type,

            "credit_score":
                credit_score,

            "customer_segment":
                customer_segment,

            "branch_location":
                branch_location
        }


        records.append(
            record
        )


    return records



def validate_dataset(
    records: List[Dict]
) -> None:

    """
    Validate generated data against capstone requirements.
    """

    assert records, (
        "Dataset cannot be empty."
    )


    required_fields = {

        "record_id",

        "category",

        "status",

        "loan_amount_inr",

        "days_since_created",

        "flagged_for_fraud_review"
    }


    for record in records:

        missing_fields = (
            required_fields
            -
            set(
                record.keys()
            )
        )


        assert not missing_fields, (
            "Missing required fields: "
            f"{missing_fields}"
        )


    record_ids = [

        record[
            "record_id"
        ]

        for record in records
    ]


    assert (
        len(
            record_ids
        )
        ==
        len(
            set(
                record_ids
            )
        )
    ), (
        "record_id values must be unique."
    )


    category_counts = {

        category:
            sum(
                1
                for record in records

                if record[
                    "category"
                ]
                ==
                category
            )

        for category in loan_types
    }


    status_counts = {

        status:
            sum(
                1
                for record in records

                if record[
                    "status"
                ]
                ==
                status
            )

        for status in repayment_statuses
    }


    fraud_count = sum(

        1

        for record in records

        if record[
            "flagged_for_fraud_review"
        ]
    )


    fraud_percentage = (

        fraud_count

        /

        len(
            records
        )

        *

        100
    )


    for category, count in (
        category_counts.items()
    ):

        assert count >= 3, (

            f"Category '{category}' "
            f"has only {count} records."
        )


    for status, count in (
        status_counts.items()
    ):

        assert count >= 1, (

            f"Status '{status}' "
            f"has no records."
        )


    assert (
        10.0
        <=
        fraud_percentage
        <=
        30.0
    ), (

        "Fraud review percentage "
        f"{fraud_percentage:.2f}% "
        "must be between 10% and 30%."
    )


    for record in records:

        assert (
            record[
                "category"
            ]
            in
            loan_types
        )


        assert (
            record[
                "status"
            ]
            in
            repayment_statuses
        )


        assert (
            record[
                "loan_amount_inr"
            ]
            >
            0
        )


        assert (
            0
            <=
            record[
                "days_since_created"
            ]
            <=
            30
        )


        assert isinstance(
            record[
                "flagged_for_fraud_review"
            ],
            bool
        )


    print(
        "=" * 70
    )

    print(
        "DATASET GENERATION REPORT"
    )

    print(
        "=" * 70
    )


    print(
        f"Seed: {SEED}"
    )


    print(
        f"Total Records: {len(records)}"
    )


    print(
        f"Category Counts: {category_counts}"
    )


    print(
        f"Status Counts: {status_counts}"
    )


    print(
        "Fraud Review Rate: "
        f"{fraud_count} "
        f"({fraud_percentage:.2f}%)"
    )


    print(
        "Loan Amount Range: "
        f"₹{min(r['loan_amount_inr'] for r in records):,}"
        " - "
        f"₹{max(r['loan_amount_inr'] for r in records):,}"
    )


def save_dataset(
    records: List[Dict]
) -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    with open(
        JSON_OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            records,
            json_file,
            indent=2,
            ensure_ascii=False
        )


    with open(
        CSV_OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(
                records[
                    0
                ].keys()
            )
        )


        writer.writeheader()


        writer.writerows(
            records
        )


    print(
        "\nDataset saved successfully:"
    )

    print(
        f"JSON : {JSON_OUTPUT_PATH}"
    )

    print(
        f"CSV  : {CSV_OUTPUT_PATH}"
    )

    print(
        "\nExisting Banking.csv was not modified."
    )


def validate_and_save() -> None:

    records = generate_loan_dataset(
        seed=SEED,
        count=RECORD_COUNT
    )


    validate_dataset(
        records
    )


    save_dataset(
        records
    )


if __name__ == "__main__":

    validate_and_save()
