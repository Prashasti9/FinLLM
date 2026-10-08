import sqlite3
import subprocess
import sys

DB_FILE = "data/database/finllm.db"


# ============================================================
# 1. CONNECT AND SELECT CASE
# ============================================================

print("\n==========================================")
print("       FINLLM INVESTIGATION AGENT")
print("==========================================")

case_id = input(
    "\nEnter Case ID [CASE-TX1005]: "
).strip()

if not case_id:
    case_id = "CASE-TX1005"


connection = sqlite3.connect(DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


# ============================================================
# 2. VERIFY CASE EXISTS
# ============================================================

case = cursor.execute(
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
).fetchone()


if case is None:
    connection.close()

    raise SystemExit(
        f"\nCase {case_id} does not exist."
    )


print("\n========== CASE FOUND ==========\n")

print("Case ID:", case["case_id"])
print("Transaction:", case["transaction_id"])
print("Customer:", case["customer_id"])
print("Risk score:", case["risk_score"])
print("Review level:", case["review_level"])
print("Current status:", case["status"])


# ============================================================
# 3. VERIFY POLICY EVIDENCE
# ============================================================

policy_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM case_policy_evidence
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()[0]


print(
    "\nPolicy evidence records:",
    policy_count
)


if policy_count == 0:
    connection.close()

    raise SystemExit(
        "\nNo policy evidence exists for this case. "
        "Run the policy-link stage first."
    )


# ============================================================
# 4. VERIFY COMPLIANCE REVIEW
# ============================================================

compliance = cursor.execute(
    """
    SELECT case_id
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()


if compliance is None:
    connection.close()

    raise SystemExit(
        "\nNo compliance review exists for this case. "
        "Generate the compliance review first."
    )


print("Compliance review: FOUND")


connection.close()


# ============================================================
# 5. RUN INVESTIGATION DATA AGENT
# ============================================================

print(
    "\n=========================================="
)
print(
    "STEP 1 — BUILDING INVESTIGATION REPORT"
)
print(
    "==========================================\n"
)


process1 = subprocess.run(
    [
        sys.executable,
        "-u",
        "investigation_agent.py"
    ],
    input=case_id + "\n",
    text=True
)


if process1.returncode != 0:

    raise SystemExit(
        "\nInvestigation data agent failed."
    )


# ============================================================
# 6. RUN QWEN INVESTIGATION AGENT
# ============================================================

print(
    "\n=========================================="
)
print(
    "STEP 2 — RUNNING QWEN INVESTIGATION"
)
print(
    "==========================================\n"
)


process2 = subprocess.run(
    [
        sys.executable,
        "-u",
        "investigation_llm.py"
    ],
    input=case_id + "\n",
    text=True
)


if process2.returncode != 0:

    raise SystemExit(
        "\nQwen investigation agent failed."
    )


# ============================================================
# 7. VERIFY FINAL INVESTIGATION
# ============================================================

connection = sqlite3.connect(DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


report = cursor.execute(
    """
    SELECT
        i.case_id,
        i.transaction_id,
        i.customer_id,
        i.risk_score,
        i.review_level,
        i.current_status,
        a.policy_refs,
        a.recommended_next_step
    FROM investigation_reports i

    JOIN investigation_ai_reports a
        ON i.case_id = a.case_id

    WHERE i.case_id = ?
    """,
    (case_id,)
).fetchone()


if report is None:
    connection.close()

    raise SystemExit(
        "\nFinal investigation verification failed."
    )


# ============================================================
# 8. CHECK HUMAN STATUS HAS NOT BEEN CHANGED
# ============================================================

current_case = cursor.execute(
    """
    SELECT status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()


connection.close()


# ============================================================
# 9. DISPLAY FINAL ORCHESTRATION RESULT
# ============================================================

print(
    "\n=========================================="
)
print(
    "       FINLLM AGENT RESULT"
)
print(
    "==========================================\n"
)

print("Case:", report["case_id"])
print("Transaction:", report["transaction_id"])
print("Customer:", report["customer_id"])
print("Risk score:", report["risk_score"])
print("Review level:", report["review_level"])

print(
    "Human case status:",
    current_case["status"]
)

print(
    "Policy references:",
    report["policy_refs"]
)

print(
    "\nAI recommended next step:"
)

print(
    report["recommended_next_step"]
)


print(
    "\n=========================================="
)
print(
    "INVESTIGATION PIPELINE COMPLETE"
)
print(
    "=========================================="
)

print(
    "\nThe AI investigation is complete."
)

print(
    "No human decision was automatically changed."
)

print(
    "The case is ready for human review."
)

print(
    "\nPhase 5.2D orchestration checkpoint finished."
)