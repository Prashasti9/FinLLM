import os
import sqlite3
import subprocess
import sys

DB_FILE = "data/database/finllm.db"


# ============================================================
# HELPER — RUN A PYTHON SCRIPT
# ============================================================

def run_script(script_name, user_input=None):

    print("\n==========================================")
    print(f"RUNNING: {script_name}")
    print("==========================================\n")

    if not os.path.exists(script_name):
        raise SystemExit(
            f"Required script not found: {script_name}"
        )

    result = subprocess.run(
        [
            sys.executable,
            "-u",
            script_name
        ],
        input=user_input,
        text=True
    )

    if result.returncode != 0:
        raise SystemExit(
            f"\n{script_name} failed with "
            f"exit code {result.returncode}."
        )

    print(
        f"\n{script_name} completed successfully."
    )


# ============================================================
# HELPER — CONNECT TO SQLITE
# ============================================================

def connect_db():

    if not os.path.exists(DB_FILE):
        raise SystemExit(
            f"Database not found: {DB_FILE}"
        )

    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# START
# ============================================================

print("\n==========================================")
print("       FINLLM CASE PIPELINE")
print("==========================================")

print(
    "\nThis pipeline will prepare a case for "
    "human review."
)

print(
    "It will NOT automatically make a human "
    "compliance decision."
)


# ============================================================
# 1. RUN RISK ENGINE
# ============================================================

run_script(
    "risk_engine.py"
)


# ============================================================
# 2. CREATE / REFRESH REVIEW CASES
# ============================================================

run_script(
    "create_review_cases.py"
)


# ============================================================
# 3. FIND DEFAULT HIGH-RISK CASE
# ============================================================

connection = connect_db()
cursor = connection.cursor()

default_case = cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        case_status
    FROM review_cases
    WHERE review_level = 'HIGH'
    ORDER BY
        risk_score DESC,
        created_at DESC
    LIMIT 1
    """
).fetchone()

connection.close()


if default_case is None:
    print("\n==========================================")
    print("NO HIGH-RISK CASE FOUND")
    print("==========================================")

    print(
        "\nRisk scoring completed, but no HIGH-risk "
        "case currently requires investigation."
    )

    print(
        "\nCase pipeline finished safely."
    )

    raise SystemExit(0)


default_case_id = default_case["case_id"]


print("\n========== HIGH-RISK CASE FOUND ==========\n")

print("Case:", default_case["case_id"])
print("Transaction:", default_case["transaction_id"])
print("Customer:", default_case["customer_id"])
print("Risk score:", default_case["risk_score"])
print("Review level:", default_case["review_level"])
print("Current human status:", default_case["case_status"])


# ============================================================
# 4. ALLOW CASE SELECTION
# ============================================================

case_id = input(
    f"\nEnter Case ID [{default_case_id}]: "
).strip()

if not case_id:
    case_id = default_case_id


connection = connect_db()
cursor = connection.cursor()

case = cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons,
        case_status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

connection.close()


if case is None:
    raise SystemExit(
        f"\nCase {case_id} does not exist."
    )


print("\n========== SELECTED CASE ==========\n")

print("Case:", case["case_id"])
print("Transaction:", case["transaction_id"])
print("Customer:", case["customer_id"])
print("Risk score:", case["risk_score"])
print("Review level:", case["review_level"])
print("Current human status:", case["case_status"])


# ============================================================
# 5. CHECK / CREATE POLICY EVIDENCE
# ============================================================

connection = connect_db()
cursor = connection.cursor()

policy_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM case_policy_evidence
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()[0]

connection.close()


if policy_count == 0:

    print(
        "\nNo stored policy evidence found."
    )

    print(
        "Starting ChromaDB policy retrieval..."
    )

    run_script(
        "link_case_policy.py",
        case_id + "\n"
    )

else:

    print(
        f"\nPolicy evidence already exists "
        f"({policy_count} records)."
    )

    print(
        "Skipping policy-link generation."
    )


# ============================================================
# 6. VERIFY POLICY EVIDENCE
# ============================================================

connection = connect_db()
cursor = connection.cursor()

policy_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM case_policy_evidence
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()[0]

connection.close()


if policy_count == 0:
    raise SystemExit(
        "\nPolicy evidence could not be established."
    )


print(
    f"Verified policy evidence records: "
    f"{policy_count}"
)


# ============================================================
# 7. CHECK / CREATE COMPLIANCE REVIEW
# ============================================================

connection = connect_db()
cursor = connection.cursor()

compliance_review = cursor.execute(
    """
    SELECT case_id
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

connection.close()


if compliance_review is None:

    print(
        "\nNo compliance review found."
    )

    print(
        "Generating FinLLM compliance review..."
    )

    run_script(
        "case_compliance_explanation.py",
        case_id + "\n"
    )

else:

    print(
        "\nCompliance review already exists."
    )

    print(
        "Skipping compliance-review generation."
    )


# ============================================================
# 8. VERIFY COMPLIANCE REVIEW
# ============================================================

connection = connect_db()
cursor = connection.cursor()

compliance_review = cursor.execute(
    """
    SELECT
        case_id,
        summary,
        policy_relevance,
        recommended_action,
        policy_refs
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

connection.close()


if compliance_review is None:
    raise SystemExit(
        "\nCompliance review verification failed."
    )


print(
    "\nCompliance review verified."
)

print(
    "Policy references:",
    compliance_review["policy_refs"]
)


# ============================================================
# 9. SAVE HUMAN STATUS BEFORE AI INVESTIGATION
# ============================================================

connection = connect_db()
cursor = connection.cursor()

status_before = cursor.execute(
    """
    SELECT case_status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

connection.close()


if status_before is None:
    raise SystemExit(
        "\nCould not verify current human case status."
    )


status_before = status_before["case_status"]


# ============================================================
# 10. RUN INVESTIGATION ORCHESTRATOR
# ============================================================

print("\n==========================================")
print("STARTING INVESTIGATION AGENT")
print("==========================================")

run_script(
    "investigation_orchestrator.py",
    case_id + "\n"
)


# ============================================================
# 11. VERIFY INVESTIGATION OUTPUT
# ============================================================

connection = connect_db()
cursor = connection.cursor()

investigation = cursor.execute(
    """
    SELECT
        case_id,
        policy_refs,
        recommended_next_step
    FROM investigation_ai_reports
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()


status_after_row = cursor.execute(
    """
    SELECT case_status
    FROM review_cases
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

connection.close()


if investigation is None:
    raise SystemExit(
        "\nAI investigation verification failed."
    )


if status_after_row is None:
    raise SystemExit(
        "\nCould not verify final human case status."
    )


status_after = status_after_row["case_status"]


# ============================================================
# 12. HUMAN-DECISION SAFETY CHECK
# ============================================================

if status_before != status_after:

    raise SystemExit(
        "\nSAFETY CHECK FAILED:\n"
        f"Human case status changed from "
        f"{status_before} to {status_after} "
        f"during AI investigation."
    )


# ============================================================
# 13. FINAL RESULT
# ============================================================

print("\n==========================================")
print("       CASE PIPELINE COMPLETE")
print("==========================================\n")

print("Case:", case_id)
print("Transaction:", case["transaction_id"])
print("Customer:", case["customer_id"])
print("Risk score:", case["risk_score"])
print("Review level:", case["review_level"])

print(
    "Human case status:",
    status_after
)

print(
    "Policy references:",
    investigation["policy_refs"]
)

print(
    "\nAI recommended next step:"
)

print(
    investigation["recommended_next_step"]
)


print("\n==========================================")
print("       HUMAN DECISION BOUNDARY")
print("==========================================")

print(
    "\nAutomated analysis is complete."
)

print(
    "No human case decision was automatically changed."
)

print(
    "The case is now ready for a human reviewer."
)

print(
    "\nTo make a human decision later, use:"
)

print(
    "python -u .\\case_decision_cli.py"
)

print(
    "\nPhase 5.3B full case-pipeline "
    "checkpoint finished."
)