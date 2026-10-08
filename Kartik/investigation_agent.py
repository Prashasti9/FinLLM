import sqlite3
from datetime import datetime, timezone

DB_FILE = "data/database/finllm.db"

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# ============================================================
# 1. SELECT CASE
# ============================================================

case_id = input(
    "\nEnter Case ID [CASE-TX1005]: "
).strip()

if not case_id:
    case_id = "CASE-TX1005"

case_row = cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        case_status,
        status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

if case_row is None:
    connection.close()
    raise SystemExit(
        f"Case {case_id} was not found."
    )

transaction_id = case_row["transaction_id"]
customer_id = case_row["customer_id"]

# ============================================================
# 2. LOAD TRANSACTION ANALYSIS
# ============================================================

transaction = cursor.execute(
    """
    SELECT
        transaction_id,
        customer_id,
        timestamp,
        amount,
        transaction_type,
        country,
        beneficiary_id,
        device_id,
        channel,
        baseline_average,
        amount_vs_baseline
    FROM transaction_analysis
    WHERE transaction_id = ?
    """,
    (transaction_id,)
).fetchone()

if transaction is None:
    connection.close()
    raise SystemExit(
        f"Transaction {transaction_id} was not found."
    )

# ============================================================
# 3. LOAD CUSTOMER SUMMARY
# ============================================================

customer = cursor.execute(
    """
    SELECT
        customer_id,
        transaction_count,
        total_amount,
        average_amount,
        minimum_amount,
        maximum_amount
    FROM customer_summary
    WHERE customer_id = ?
    """,
    (customer_id,)
).fetchone()

# ============================================================
# 4. LOAD COMPLIANCE REVIEW
# ============================================================

compliance = cursor.execute(
    """
    SELECT
        case_id,
        summary,
        transaction_observation,
        policy_relevance,
        recommended_action,
        policy_refs
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

# ============================================================
# 5. LOAD POLICY EVIDENCE
# ============================================================

policy_evidence = cursor.execute(
    """
    SELECT
        id,
        source,
        page,
        jurisdiction,
        content
    FROM case_policy_evidence
    WHERE case_id = ?
    ORDER BY id
    """,
    (case_id,)
).fetchall()

# ============================================================
# 6. LOAD AUDIT HISTORY
# ============================================================

audit_history = cursor.execute(
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
).fetchall()

# ============================================================
# 7. CREATE INVESTIGATION REPORT TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS investigation_reports (
        case_id TEXT PRIMARY KEY,
        transaction_id TEXT,
        customer_id TEXT,
        risk_score INTEGER,
        review_level TEXT,
        current_status TEXT,
        investigation_summary TEXT,
        policy_refs TEXT,
        generated_at TEXT
    )
    """
)

# ============================================================
# 8. BUILD DETERMINISTIC INVESTIGATION SUMMARY
# ============================================================

current_status = (
    case_row["status"]
    or case_row["case_status"]
    or "UNKNOWN"
)

risk_score = case_row["risk_score"]
review_level = case_row["review_level"]
risk_reasons = case_row["risk_reasons"]

summary_lines = []

summary_lines.append(
    f"Case {case_id} concerns transaction "
    f"{transaction_id} for customer {customer_id}."
)

summary_lines.append(
    f"The transaction amount is "
    f"${transaction['amount']:.2f}."
)

summary_lines.append(
    f"The customer's calculated baseline average is "
    f"${transaction['baseline_average']:.2f}, "
    f"giving an amount-to-baseline ratio of "
    f"{transaction['amount_vs_baseline']:.2f}x."
)

summary_lines.append(
    f"The rule-based risk score is {risk_score} "
    f"with review level {review_level}."
)

summary_lines.append(
    f"Recorded risk reasons: {risk_reasons}."
)

summary_lines.append(
    f"The transaction country code is "
    f"{transaction['country']} and device ID is "
    f"{transaction['device_id']}."
)

if customer is not None:
    summary_lines.append(
        f"Customer {customer_id} has "
        f"{customer['transaction_count']} transactions "
        f"with total amount ${customer['total_amount']:.2f} "
        f"and average amount "
        f"${customer['average_amount']:.2f}."
    )

if compliance is not None:
    summary_lines.append(
        "A compliance review has been generated and "
        "linked to policy evidence."
    )

if audit_history:
    summary_lines.append(
        f"The case has {len(audit_history)} "
        f"recorded human decision event(s)."
    )

summary_lines.append(
    f"The current case status is {current_status}."
)

summary_lines.append(
    "The risk score is a review indicator and does not "
    "by itself establish fraud or wrongdoing."
)

investigation_summary = " ".join(summary_lines)

policy_refs = ""

if compliance is not None:
    policy_refs = compliance["policy_refs"] or ""

generated_at = datetime.now(
    timezone.utc
).isoformat()

# ============================================================
# 9. SAVE INVESTIGATION REPORT
# ============================================================

cursor.execute(
    """
    INSERT INTO investigation_reports (
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        current_status,
        investigation_summary,
        policy_refs,
        generated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT(case_id)
    DO UPDATE SET
        transaction_id = excluded.transaction_id,
        customer_id = excluded.customer_id,
        risk_score = excluded.risk_score,
        review_level = excluded.review_level,
        current_status = excluded.current_status,
        investigation_summary =
            excluded.investigation_summary,
        policy_refs = excluded.policy_refs,
        generated_at = excluded.generated_at
    """,
    (
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        current_status,
        investigation_summary,
        policy_refs,
        generated_at
    )
)

connection.commit()

# ============================================================
# 10. DISPLAY INVESTIGATION REPORT
# ============================================================

print(
    "\n========== FINLLM INVESTIGATION ==========\n"
)

print("Case ID:", case_id)
print("Transaction:", transaction_id)
print("Customer:", customer_id)
print("Risk score:", risk_score)
print("Review level:", review_level)
print("Current status:", current_status)

print("\n---------- TRANSACTION ----------\n")

print("Amount:", transaction["amount"])
print(
    "Baseline average:",
    round(transaction["baseline_average"], 2)
)
print(
    "Deviation ratio:",
    round(transaction["amount_vs_baseline"], 2)
)
print("Country:", transaction["country"])
print("Device:", transaction["device_id"])
print("Channel:", transaction["channel"])

print("\n---------- RISK REASONS ----------\n")

print(risk_reasons)

print("\n---------- INVESTIGATION SUMMARY ----------\n")

print(investigation_summary)

print("\n---------- COMPLIANCE REVIEW ----------\n")

if compliance is None:
    print("No compliance review found.")
else:
    print("Summary:")
    print(compliance["summary"])

    print("\nPolicy relevance:")
    print(compliance["policy_relevance"])

    print("\nRecommended action:")
    print(compliance["recommended_action"])

    print(
        "\nPolicy references:",
        compliance["policy_refs"]
    )

print("\n---------- POLICY EVIDENCE ----------\n")

if not policy_evidence:
    print("No policy evidence found.")
else:
    for index, item in enumerate(
        policy_evidence,
        start=1
    ):
        print(
            f"[P{index}] "
            f"{item['source']}, "
            f"PDF page {item['page']}, "
            f"{item['jurisdiction']}"
        )

print("\n---------- HUMAN AUDIT HISTORY ----------\n")

if not audit_history:
    print("No human decisions recorded.")
else:
    for audit in audit_history:

        print(
            f"Audit {audit['audit_id']}: "
            f"{audit['old_status']} -> "
            f"{audit['new_status']}"
        )

        print(
            "Reviewer:",
            audit["reviewer"]
        )

        print(
            "Note:",
            audit["note"]
        )

        print(
            "Time:",
            audit["changed_at"]
        )

        print("-" * 50)

print(
    "\nInvestigation report saved to SQLite."
)

print(
    "Phase 5.2 investigation-agent "
    "checkpoint finished."
)

connection.close()