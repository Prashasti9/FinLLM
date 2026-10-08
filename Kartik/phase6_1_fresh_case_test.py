import csv
import os
import subprocess
import sys

CSV_FILE = "data/transactions/transactions.csv"

NEW_TRANSACTIONS = [
    [
        "TX1011", "C003", "2026-10-01 09:00:00",
        "200.00", "TRANSFER", "US", "B010", "D010", "WEB"
    ],
    [
        "TX1012", "C003", "2026-10-02 10:00:00",
        "220.00", "TRANSFER", "US", "B010", "D010", "WEB"
    ],
    [
        "TX1013", "C003", "2026-10-03 11:00:00",
        "210.00", "PAYMENT", "US", "B010", "D010", "MOBILE"
    ],
    [
        "TX1014", "C003", "2026-10-04 12:00:00",
        "205.00", "TRANSFER", "US", "B010", "D010", "WEB"
    ],
    [
        "TX1015", "C003", "2026-10-05 13:00:00",
        "7800.00", "TRANSFER", "GB", "B099", "D099", "WEB"
    ]
]


def existing_transaction_ids():

    ids = set()

    if not os.path.exists(CSV_FILE):
        raise SystemExit(
            f"Could not find {CSV_FILE}"
        )

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            ids.add(
                row["transaction_id"].strip()
            )

    return ids


def append_transactions():

    existing = existing_transaction_ids()

    added = 0

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        for row in NEW_TRANSACTIONS:

            if row[0] not in existing:

                writer.writerow(row)

                print(
                    f"Added {row[0]}"
                )

                added += 1

            else:

                print(
                    f"{row[0]} already exists — skipped"
                )

    print(
        f"\nTransactions added: {added}"
    )


def run_script(script_name):

    print(
        f"\n========== RUNNING {script_name} ==========\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-u",
            script_name
        ]
    )

    if result.returncode != 0:
        raise SystemExit(
            f"{script_name} failed."
        )


print(
    "\n========== PHASE 6.1 FRESH CASE TEST ==========\n"
)

append_transactions()

run_script(
    "analyze_transactions.py"
)

run_script(
    "load_transactions_db.py"
)

run_script(
    "risk_engine.py"
)

run_script(
    "create_review_cases.py"
)

print(
    "\n=============================================="
)
print(
    "PHASE 6.1 DATA PREPARATION COMPLETE"
)
print(
    "Expected high-risk transaction: TX1015"
)
print(
    "Expected case: CASE-TX1015"
)
print(
    "=============================================="
)