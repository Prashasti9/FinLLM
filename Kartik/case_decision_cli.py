import sqlite3
from datetime import datetime, timezone

DB_FILE = "data/database/finllm.db"

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


# ============================================================
# 1. MAKE SURE REVIEW CASE HAS STATUS COLUMN
# ============================================================

cursor.execute("PRAGMA table_info(review_cases)")
columns = [row[1] for row in cursor.fetchall()]

if "status" not in columns:
    cursor.execute(
        """
        ALTER TABLE review_cases
        ADD COLUMN status TEXT DEFAULT 'OPEN'
        """
    )
    connection.commit()


# ============================================================
# 2. CREATE AUDIT LOG TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS case_audit_log (

        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

        case_id TEXT NOT NULL,

        old_status TEXT,

        new_status TEXT NOT NULL,

        reviewer TEXT NOT NULL,

        note TEXT,

        changed_at TEXT NOT NULL
    )
    """
)

connection.commit()


# ============================================================
# 3. ASK FOR CASE
# ============================================================

case_id = input(
    "\nEnter Case ID [CASE-TX1005]: "
).strip()

if not case_id:
    case_id = "CASE-TX1005"


# ============================================================
# 4. LOAD CASE
# ============================================================

cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
)

case = cursor.fetchone()

if case is None:
    connection.close()
    raise SystemExit(
        f"Case not found: {case_id}"
    )


(
    case_id,
    transaction_id,
    customer_id,
    risk_score,
    review_level,
    risk_reasons,
    current_status
) = case


if not current_status:
    current_status = "OPEN"


# ============================================================
# 5. DISPLAY CASE
# ============================================================

print("\n========== CASE FOR HUMAN REVIEW ==========\n")

print("Case ID:", case_id)
print("Transaction:", transaction_id)
print("Customer:", customer_id)
print("Risk score:", risk_score)
print("Review level:", review_level)
print("Current status:", current_status)
print("Risk reasons:", risk_reasons)


# ============================================================
# 6. LOAD FINLLM COMPLIANCE REVIEW
# ============================================================

cursor.execute(
    """
    SELECT
        summary,
        policy_relevance,
        recommended_action,
        policy_refs
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
)

review = cursor.fetchone()

if review:

    (
        summary,
        policy_relevance,
        recommended_action,
        policy_refs
    ) = review

    print(
        "\n========== FINLLM DECISION SUPPORT ==========\n"
    )

    print("Summary:")
    print(summary)

    print("\nPolicy relevance:")
    print(policy_relevance)

    print("\nRecommended action:")
    print(recommended_action)

    print("\nPolicy references:")
    print(policy_refs)

else:

    print(
        "\nNo FinLLM compliance review found for this case."
    )


# ============================================================
# 7. HUMAN DECISION
# ============================================================

print("\n========== HUMAN DECISION ==========\n")

print("1 - UNDER_REVIEW")
print("2 - ESCALATED")
print("3 - CLOSED")
print("4 - OPEN")

choice = input(
    "\nSelect decision (1-4): "
).strip()


status_map = {
    "1": "UNDER_REVIEW",
    "2": "ESCALATED",
    "3": "CLOSED",
    "4": "OPEN"
}


if choice not in status_map:
    connection.close()
    raise SystemExit(
        "Invalid decision. No changes were made."
    )


new_status = status_map[choice]


reviewer = input(
    "Reviewer name: "
).strip()

if not reviewer:
    connection.close()
    raise SystemExit(
        "Reviewer name is required."
    )


note = input(
    "Review note: "
).strip()

if not note:
    note = "No additional note provided."


# ============================================================
# 8. UPDATE CASE STATUS
# ============================================================

cursor.execute(
    """
    UPDATE review_cases
    SET case_status = ?
    WHERE case_id = ?
    """,
    (
        new_status,
        case_id
    )
)


# ============================================================
# 9. WRITE AUDIT LOG
# ============================================================

changed_at = datetime.now(
    timezone.utc
).isoformat()


cursor.execute(
    """
    INSERT INTO case_audit_log (
        case_id,
        old_status,
        new_status,
        reviewer,
        note,
        changed_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        case_id,
        current_status,
        new_status,
        reviewer,
        note,
        changed_at
    )
)


connection.commit()


# ============================================================
# 10. VERIFY CHANGE
# ============================================================

cursor.execute(
    """
    SELECT case_status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
)

saved_status = cursor.fetchone()[0]


print(
    "\n========== DECISION SAVED ==========\n"
)

print("Case:", case_id)
print("Previous status:", current_status)
print("New status:", saved_status)
print("Reviewer:", reviewer)
print("Timestamp:", changed_at)


# ============================================================
# 11. SHOW AUDIT HISTORY
# ============================================================

print(
    "\n========== CASE AUDIT HISTORY ==========\n"
)

cursor.execute(
    """
    SELECT
        audit_id,
        old_status,
        new_status,
        reviewer,
        note,
        changed_at
    FROM case_audit_log
    WHERE case_id = ?
    ORDER BY audit_id
    """,
    (case_id,)
)


for row in cursor.fetchall():

    print(
        f"Audit ID: {row[0]}"
    )

    print(
        f"{row[1]} -> {row[2]}"
    )

    print(
        f"Reviewer: {row[3]}"
    )

    print(
        f"Note: {row[4]}"
    )

    print(
        f"Time: {row[5]}"
    )

    print(
        "-" * 50
    )


connection.close()

print(
    "\nPhase 4.5 human-decision and audit-trail test finished."
)