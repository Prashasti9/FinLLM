import sqlite3
from datetime import datetime

DB_FILE = "data/database/finllm.db"

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


# ==================================================
# 1. CREATE REVIEW CASE TABLE
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS review_cases (

    case_id TEXT PRIMARY KEY,

    transaction_id TEXT UNIQUE NOT NULL,

    customer_id TEXT NOT NULL,

    risk_score INTEGER NOT NULL,

    review_level TEXT NOT NULL,

    risk_reasons TEXT NOT NULL,

    case_status TEXT NOT NULL,

    created_at TEXT NOT NULL
)
""")

connection.commit()

print("Review-case table ready.")


# ==================================================
# 2. FIND HIGH-RISK TRANSACTIONS
# ==================================================

cursor.execute("""
SELECT
    transaction_id,
    customer_id,
    risk_score,
    review_level,
    risk_reasons
FROM risk_scores
WHERE review_level = 'HIGH'
ORDER BY risk_score DESC
""")

high_risk_transactions = cursor.fetchall()

print(
    f"High-risk transactions found: "
    f"{len(high_risk_transactions)}"
)


# ==================================================
# 3. CREATE REVIEW CASES
# ==================================================

for row in high_risk_transactions:

    transaction_id = row[0]
    customer_id = row[1]
    risk_score = row[2]
    review_level = row[3]
    risk_reasons = row[4]

    case_id = f"CASE-{transaction_id}"

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor.execute("""
    INSERT OR IGNORE INTO review_cases (
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        case_status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        "OPEN",
        created_at
    ))

connection.commit()


# ==================================================
# 4. DISPLAY REVIEW CASES
# ==================================================

cursor.execute("""
SELECT
    case_id,
    transaction_id,
    customer_id,
    risk_score,
    review_level,
    case_status,
    risk_reasons
FROM review_cases
ORDER BY risk_score DESC
""")

cases = cursor.fetchall()

print("\n========== REVIEW CASES ==========\n")

if not cases:

    print("No review cases created.")

else:

    for case in cases:

        print("Case ID:", case[0])
        print("Transaction:", case[1])
        print("Customer:", case[2])
        print("Risk score:", case[3])
        print("Review level:", case[4])
        print("Status:", case[5])
        print("Reasons:", case[6])

        print("-" * 60)


# ==================================================
# 5. FINISH
# ==================================================

connection.close()

print("\nPhase 4.2 review-case test finished.")