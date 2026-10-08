import sqlite3
import json
from datetime import datetime, timezone

import ollama


DB_FILE = "data/database/finllm.db"
MODEL = "qwen3:4b"


# ============================================================
# 1. CONNECT TO DATABASE
# ============================================================

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


# ============================================================
# 2. SELECT CASE
# ============================================================

case_id = input(
    "\nEnter Case ID [CASE-TX1005]: "
).strip()

if not case_id:
    case_id = "CASE-TX1005"


# ============================================================
# 3. LOAD VERIFIED INVESTIGATION
# ============================================================

investigation = cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        current_status,
        investigation_summary,
        policy_refs
    FROM investigation_reports
    WHERE case_id = ?
    """,
    (case_id,)
).fetchone()

if investigation is None:
    connection.close()

    raise SystemExit(
        f"No investigation report found for {case_id}. "
        "Run investigation_agent.py first."
    )


transaction_id = investigation["transaction_id"]


# ============================================================
# 4. LOAD TRANSACTION FACTS
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
# 5. LOAD COMPLIANCE REVIEW
# ============================================================

compliance = cursor.execute(
    """
    SELECT
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
# 6. LOAD POLICY EVIDENCE
# ============================================================

policy_rows = cursor.execute(
    """
    SELECT
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
# 7. LOAD HUMAN AUDIT HISTORY
# ============================================================

audit_rows = cursor.execute(
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
# 8. BUILD POLICY EVIDENCE
# ============================================================

policy_blocks = []
available_refs = []

for index, row in enumerate(policy_rows, start=1):

    label = f"P{index}"
    available_refs.append(label)

    policy_blocks.append(
        f"""
[{label}]
Source: {row['source']}
PDF page: {row['page']}
Jurisdiction: {row['jurisdiction']}
Content:
{row['content']}
""".strip()
    )

policy_text = "\n\n".join(policy_blocks)


# ============================================================
# 9. BUILD HUMAN AUDIT EVIDENCE
# ============================================================

audit_blocks = []

for row in audit_rows:

    audit_blocks.append(
        f"""
Audit ID: {row['audit_id']}
Status change: {row['old_status']} -> {row['new_status']}
Reviewer: {row['reviewer']}
Note: {row['note']}
Time: {row['changed_at']}
""".strip()
    )

audit_text = "\n\n".join(audit_blocks)

if not audit_text:
    audit_text = "No human decision events recorded."


# ============================================================
# 10. BUILD COMPLIANCE EVIDENCE
# ============================================================

if compliance is not None:

    compliance_text = f"""
Summary:
{compliance['summary']}

Transaction observation:
{compliance['transaction_observation']}

Policy relevance:
{compliance['policy_relevance']}

Recommended action:
{compliance['recommended_action']}

Policy references:
{compliance['policy_refs']}
"""

else:

    compliance_text = "No compliance review exists."


# ============================================================
# 11. BUILD VERIFIED CASE EVIDENCE
# ============================================================

evidence = f"""
CASE
Case ID: {investigation['case_id']}
Transaction ID: {investigation['transaction_id']}
Customer ID: {investigation['customer_id']}
Risk score: {investigation['risk_score']}
Review level: {investigation['review_level']}
Current human status: {investigation['current_status']}

TRANSACTION
Timestamp: {transaction['timestamp']}
Amount: {transaction['amount']}
Transaction type: {transaction['transaction_type']}
Country code: {transaction['country']}
Beneficiary ID: {transaction['beneficiary_id']}
Device ID: {transaction['device_id']}
Channel: {transaction['channel']}
Baseline average: {transaction['baseline_average']}
Amount vs baseline: {transaction['amount_vs_baseline']}

VERIFIED INVESTIGATION SUMMARY
{investigation['investigation_summary']}

COMPLIANCE REVIEW
{compliance_text}

POLICY EVIDENCE
{policy_text}

HUMAN AUDIT HISTORY
{audit_text}
"""


# ============================================================
# 12. STRUCTURED OUTPUT SCHEMA
# ============================================================

policy_ref_item = {
    "type": "string"
}

if available_refs:
    policy_ref_item["enum"] = available_refs


answer_schema = {
    "type": "object",
    "properties": {

        "executive_summary": {
            "type": "string"
        },

        "key_findings": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "items": {
                "type": "string"
            }
        },

        "policy_refs": {
            "type": "array",
            "items": policy_ref_item
        },

        "recommended_next_step": {
            "type": "string"
        },

        "limitations": {
            "type": "string"
        }
    },

    "required": [
        "executive_summary",
        "key_findings",
        "policy_refs",
        "recommended_next_step",
        "limitations"
    ],

    "additionalProperties": False
}


# ============================================================
# 13. GENERATE QWEN INVESTIGATION ANALYSIS
# ============================================================

print(
    "\nGenerating Qwen investigation analysis..."
)

response = ollama.chat(
    model=MODEL,
    think=False,
    stream=False,
    format=answer_schema,

    messages=[
        {
            "role": "system",
            "content": (
                "You are the FinLLM Investigation Agent. "
                "You provide financial compliance decision support. "

                "Use ONLY the supplied database and policy evidence. "

                "Do not invent transactions, customer history, "
                "laws, thresholds, policy requirements, or facts. "

                "Do not declare that fraud, money laundering, "
                "criminal activity, or wrongdoing occurred. "

                "A risk score is only a review indicator. "

                "Do not override or change the human case status. "

                "Policy references must come only from the supplied "
                "P labels. "

                "Explain why the available evidence may warrant "
                "human review, additional verification, or continued "
                "monitoring. "

                "Keep the analysis concise and factual."
            )
        },

        {
            "role": "user",
            "content": (
                "/no_think\n\n"
                "Prepare an investigation analysis from the "
                "following verified evidence:\n\n"
                + evidence
            )
        }
    ],

    options={
        "temperature": 0,
        "num_ctx": 4096,
        "num_predict": 450
    }
)


# ============================================================
# 14. PARSE STRUCTURED RESPONSE
# ============================================================

try:

    result = json.loads(
        response["message"]["content"]
    )

except json.JSONDecodeError:

    print(
        "\nFinLLM returned invalid structured output."
    )

    print(response["message"]["content"])

    connection.close()

    raise SystemExit(1)


# ============================================================
# 15. BASIC QUALITY CHECK
# ============================================================

required_fields = [
    "executive_summary",
    "key_findings",
    "policy_refs",
    "recommended_next_step",
    "limitations"
]

for field in required_fields:

    if field not in result:

        connection.close()

        raise SystemExit(
            f"Quality check failed: missing {field}"
        )


for reference in result["policy_refs"]:

    if reference not in available_refs:

        connection.close()

        raise SystemExit(
            "Quality check failed: "
            f"unsupported policy reference {reference}"
        )


combined_output = (
    result["executive_summary"]
    + " "
    + " ".join(result["key_findings"])
    + " "
    + result["recommended_next_step"]
).lower()


for forbidden in [
    "fraud occurred",
    "is fraudulent",
    "committed fraud",
    "money laundering occurred",
    "is guilty"
]:

    if forbidden in combined_output:

        connection.close()

        raise SystemExit(
            "Quality check failed: "
            "unsupported wrongdoing conclusion."
        )


# ============================================================
# 16. DISPLAY RESULT
# ============================================================

print(
    "\n========== FINLLM INVESTIGATION ANALYSIS ==========\n"
)

print("CASE:", case_id)

print(
    "\nEXECUTIVE SUMMARY:\n"
)

print(
    result["executive_summary"]
)

print(
    "\nKEY FINDINGS:"
)

for number, finding in enumerate(
    result["key_findings"],
    start=1
):

    print(
        f"{number}. {finding}"
    )


print(
    "\nPOLICY REFERENCES:"
)

if result["policy_refs"]:

    for reference in result["policy_refs"]:
        print(f"[{reference}]")

else:
    print("None")


print(
    "\nRECOMMENDED NEXT STEP:"
)

print(
    result["recommended_next_step"]
)


print(
    "\nLIMITATIONS:"
)

print(
    result["limitations"]
)


print(
    "\nGeneration stop reason:",
    response.get(
        "done_reason",
        "unknown"
    )
)


# ============================================================
# 17. SAVE VERIFIED AI INVESTIGATION
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS investigation_ai_reports (
        case_id TEXT PRIMARY KEY,
        executive_summary TEXT,
        key_findings TEXT,
        policy_refs TEXT,
        recommended_next_step TEXT,
        limitations TEXT,
        generated_at TEXT
    )
    """
)


generated_at = datetime.now(
    timezone.utc
).isoformat()


cursor.execute(
    """
    INSERT INTO investigation_ai_reports (
        case_id,
        executive_summary,
        key_findings,
        policy_refs,
        recommended_next_step,
        limitations,
        generated_at
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT(case_id)
    DO UPDATE SET

        executive_summary =
            excluded.executive_summary,

        key_findings =
            excluded.key_findings,

        policy_refs =
            excluded.policy_refs,

        recommended_next_step =
            excluded.recommended_next_step,

        limitations =
            excluded.limitations,

        generated_at =
            excluded.generated_at
    """,

    (
        case_id,

        result["executive_summary"],

        json.dumps(
            result["key_findings"]
        ),

        ",".join(
            result["policy_refs"]
        ),

        result["recommended_next_step"],

        result["limitations"],

        generated_at
    )
)


connection.commit()


print(
    "\nVerified AI investigation saved to SQLite."
)

print(
    "Phase 5.2C Qwen investigation reasoning "
    "checkpoint finished."
)


connection.close()