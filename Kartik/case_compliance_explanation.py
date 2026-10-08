import sqlite3
import json
import re
import ollama
import sys


# ============================================================
# CONFIGURATION
# ============================================================

DB_FILE = "data/database/finllm.db"

# ============================================================
# GET CASE ID
# Supports:
# 1. Command-line argument
# 2. Input passed by another Python script
# 3. Manual user input
# ============================================================

if len(sys.argv) >= 2:

    CASE_ID = sys.argv[1].strip()

elif not sys.stdin.isatty():

    CASE_ID = sys.stdin.readline().strip()

else:

    CASE_ID = input(
        "Enter Case ID: "
    ).strip()


if not CASE_ID:

    raise SystemExit(
        "Case ID cannot be empty."
    )


# ============================================================
# 1. CONNECT TO SQLITE
# ============================================================

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


# ============================================================
# 2. LOAD REVIEW CASE + TRANSACTION FACTS
# ============================================================

cursor.execute(
    """
    SELECT
        rc.case_id,
        rc.transaction_id,
        rc.customer_id,
        rc.risk_score,
        rc.review_level,
        rc.risk_reasons,
        ta.amount,
        ta.baseline_average,
        ta.amount_vs_baseline,
        ta.country,
        ta.device_id
    FROM review_cases rc
    JOIN transaction_analysis ta
        ON rc.transaction_id = ta.transaction_id
    WHERE rc.case_id = ?
    """,
    (CASE_ID,)
)

case = cursor.fetchone()

if case is None:
    connection.close()
    raise SystemExit(
        f"Case not found: {CASE_ID}"
    )


(
    case_id,
    transaction_id,
    customer_id,
    risk_score,
    review_level,
    risk_reasons,
    amount,
    baseline_average,
    amount_vs_baseline,
    country,
    device_id
) = case


print("\n========== CASE ==========\n")

print("Case ID:", case_id)
print("Transaction:", transaction_id)
print("Customer:", customer_id)
print("Risk score:", risk_score)
print("Review level:", review_level)
print("Reasons:", risk_reasons)


# ============================================================
# 3. LOAD LINKED POLICY EVIDENCE
# ============================================================

cursor.execute(
    """
    SELECT
        source,
        page,
        jurisdiction,
        content
    FROM case_policy_evidence
    WHERE case_id = ?
    ORDER BY source, page
    """,
    (CASE_ID,)
)

policy_rows = cursor.fetchall()

if len(policy_rows) < 2:
    connection.close()

    raise SystemExit(
        "Insufficient linked policy evidence."
    )


# ============================================================
# 4. BUILD POLICY REFERENCES
# ============================================================

policy_entries = []
policy_text = ""
source_details = []

for index, row in enumerate(
    policy_rows,
    start=1
):

    source = row[0]
    page = row[1]
    jurisdiction = row[2]
    content = row[3]

    label = f"P{index}"

    clean_content = " ".join(
        str(content).split()
    )

    entry = {
        "label": label,
        "source": source,
        "page": page,
        "jurisdiction": jurisdiction,
        "content": clean_content
    }

    policy_entries.append(entry)

    source_details.append(
        f"[{label}] {source}, PDF page {page}"
    )

    # Limit each excerpt so the local model is not overloaded.
    policy_text += (
        f"\n[{label}]\n"
        f"DOCUMENT: {source}\n"
        f"JURISDICTION: {jurisdiction}\n"
        f"PDF PAGE: {page}\n"
        f"EXCERPT: {clean_content[:900]}\n"
    )


# ============================================================
# 5. IDENTIFY INDIA AND U.S. POLICY REFERENCES
# ============================================================

india_labels = []
us_labels = []

for entry in policy_entries:

    jurisdiction_lower = str(
        entry["jurisdiction"]
    ).lower()

    source_lower = str(
        entry["source"]
    ).lower()

    if (
        "india" in jurisdiction_lower
        or "kyc_policy" in source_lower
    ):
        india_labels.append(
            entry["label"]
        )

    if (
        "united states" in jurisdiction_lower
        or "msb_prevention" in source_lower
    ):
        us_labels.append(
            entry["label"]
        )


if not india_labels:
    connection.close()
    raise SystemExit(
        "No Indian KYC policy evidence was found."
    )

if not us_labels:
    connection.close()
    raise SystemExit(
        "No U.S. policy evidence was found."
    )


valid_labels = [
    entry["label"]
    for entry in policy_entries
]


# ============================================================
# 6. BUILD DETERMINISTIC CASE FACTS
# ============================================================

summary = (
    f"{case_id} warrants human review because its "
    f"rule-based review score is {risk_score} with a "
    f"{review_level} review level. "
    f"The score is a review indicator and is not a "
    f"probability of wrongdoing."
)


transaction_observation = (
    f"Transaction {transaction_id} has an amount of "
    f"${amount:,.2f}, which is {amount_vs_baseline:.2f} "
    f"times the customer's calculated baseline average of "
    f"${baseline_average:,.2f}. "
    f"The stored country code is {country} and the stored "
    f"device ID is {device_id}. "
    f"The risk engine recorded the following review signals: "
    f"{risk_reasons}."
)


recommended_action = (
    "Perform human review and additional verification of the "
    "transaction context. Continue monitoring as appropriate. "
    "Do not treat the rule-based review score as an automated "
    "final compliance decision."
)


# ============================================================
# 7. JSON SCHEMA FOR QWEN
# ============================================================

answer_schema = {
    "type": "object",

    "properties": {

        "policy_relevance": {
            "type": "string"
        },

        "policy_refs": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "string",
                "enum": valid_labels
            }
        }
    },

    "required": [
        "policy_relevance",
        "policy_refs"
    ],

    "additionalProperties": False
}


# ============================================================
# 8. QUALITY CHECK
# ============================================================

def output_is_valid(
    policy_relevance,
    policy_refs
):

    if not isinstance(
        policy_relevance,
        str
    ):
        return False

    if not policy_relevance.strip():
        return False

    if not isinstance(
        policy_refs,
        list
    ):
        return False

    if len(policy_refs) < 2:
        return False


    # --------------------------------------------------------
    # Reject internal reasoning / planning language
    # --------------------------------------------------------

    forbidden_patterns = [

        r"\bi need to\b",
        r"\bi should\b",
        r"\bi must\b",
        r"\blet me\b",
        r"\bthe user\b",
        r"\bi will\b",
        r"\bi need\b",
        r"\bi'm going to\b"
    ]

    for pattern in forbidden_patterns:

        if re.search(
            pattern,
            policy_relevance,
            re.IGNORECASE
        ):
            return False


    # --------------------------------------------------------
    # Do not let model reinterpret AE as UAE
    # --------------------------------------------------------

    if re.search(
        r"\bUAE\b",
        policy_relevance,
        re.IGNORECASE
    ):
        return False


    # --------------------------------------------------------
    # Reject claims that customer has no transaction history
    # --------------------------------------------------------

    forbidden_claims = [

        "no prior transactions",
        "has no prior transactions",
        "without prior transactions",
        "no transaction history",
        "has no transaction history",
        "customer has never transacted"
    ]

    lower_relevance = (
        policy_relevance.lower()
    )

    for claim in forbidden_claims:

        if claim in lower_relevance:
            return False


    # --------------------------------------------------------
    # Reject automated accusation language
    # --------------------------------------------------------

    accusation_patterns = [

        r"\bfraud occurred\b",
        r"\bfraudulent transaction\b",
        r"\bis fraudulent\b",
        r"\bmoney laundering occurred\b",
        r"\bis money laundering\b",
        r"\bcriminal activity occurred\b",
        r"\blegal violation occurred\b"
    ]

    for pattern in accusation_patterns:

        if re.search(
            pattern,
            policy_relevance,
            re.IGNORECASE
        ):
            return False


    # --------------------------------------------------------
    # Validate returned labels
    # --------------------------------------------------------

    for ref in policy_refs:

        if ref not in valid_labels:
            return False


    # --------------------------------------------------------
    # Must use at least one India source
    # --------------------------------------------------------

    has_india_reference = any(
        ref in india_labels
        for ref in policy_refs
    )


    # --------------------------------------------------------
    # Must use at least one U.S. source
    # --------------------------------------------------------

    has_us_reference = any(
        ref in us_labels
        for ref in policy_refs
    )


    if not has_india_reference:
        return False

    if not has_us_reference:
        return False


    # --------------------------------------------------------
    # Every listed reference must appear in explanation
    # --------------------------------------------------------

    for ref in policy_refs:

        if f"[{ref}]" not in policy_relevance:
            return False


    return True


# ============================================================
# 9. GENERATE POLICY RELEVANCE WITH QWEN
# ============================================================

print(
    "\nGenerating FinLLM policy analysis..."
)

policy_result = None


for attempt in range(1, 4):

    print(
        f"Policy generation attempt "
        f"{attempt}/3..."
    )


    response = ollama.chat(

        model="qwen3:4b",

        think=False,

        stream=False,

        format=answer_schema,

        messages=[

            {
                "role": "system",

                "content": (

                    "You are FinLLM, a financial compliance "
                    "decision-support assistant. "

                    "Return only the final structured answer. "

                    "Do not show reasoning, planning, analysis, "
                    "or internal thoughts. "

                    "Use only the supplied policy excerpts. "

                    "Explain how the policy excerpts support "
                    "human review or monitoring of an unusually "
                    "large or unusual transaction pattern. "

                    "Use at least one Indian KYC reference and "
                    "at least one U.S. reference. "

                    "Place every reference directly in the "
                    "policy explanation using brackets, such as "
                    "[P1] or [P3]. "

                    "Do not invent facts or requirements. "

                    "Do not discuss the customer's country code "
                    "or device ID. "

                    "Do not say the customer has no prior "
                    "transactions. "

                    "Do not declare that fraud, money laundering, "
                    "criminal activity, or a legal violation "
                    "occurred. "

                    "Do not make an automated compliance decision. "

                    "Use no more than three concise sentences."
                )
            },

            {
                "role": "user",

                "content": (

                    "/no_think\n\n"

                    "TRANSACTION SIGNAL:\n"

                    f"Transaction {transaction_id} is "
                    f"{amount_vs_baseline:.2f} times the "
                    f"customer's calculated baseline amount.\n\n"

                    "TASK:\n"

                    "Explain only how the supplied policy excerpts "
                    "relate to monitoring or reviewing this unusually "
                    "large transaction pattern.\n\n"

                    "POLICY EVIDENCE:\n"

                    f"{policy_text}"
                )
            }
        ],

        options={
            "temperature": 0,
            "num_predict": 250,
            "num_ctx": 4096
        }
    )


    raw_content = (
        response["message"]["content"]
    )


    try:

        candidate = json.loads(
            raw_content
        )

        candidate_relevance = (
            candidate[
                "policy_relevance"
            ].strip()
        )

        candidate_refs = (
            candidate[
                "policy_refs"
            ]
        )


    except (
        json.JSONDecodeError,
        KeyError,
        TypeError
    ):

        print(
            "Attempt failed: invalid "
            "structured response."
        )

        continue


    if output_is_valid(
        candidate_relevance,
        candidate_refs
    ):

        policy_result = candidate

        print(
            "Policy quality check passed."
        )

        break


    else:

        print(
            "Attempt failed policy "
            "quality check."
        )


# ============================================================
# 10. SAFE FALLBACK
# ============================================================

if policy_result is None:

    print(
        "\nQwen output did not pass all quality checks."
    )

    print(
        "Using evidence-grounded compliance fallback."
    )


    india_ref = india_labels[0]
    us_ref = us_labels[0]


    fallback_policy_relevance = (

        f"The Indian KYC policy evidence [{india_ref}] "
        f"supports monitoring large, unusual, or otherwise "
        f"significant transaction patterns in relation to "
        f"expected customer activity. "

        f"The U.S. policy evidence [{us_ref}] also supports "
        f"attention to unusual customer or transaction activity. "

        f"Together, these excerpts support human review and "
        f"continued monitoring of the unusually large transaction "
        f"pattern, but they do not by themselves establish wrongdoing."
    )


    policy_result = {

        "policy_relevance":
            fallback_policy_relevance,

        "policy_refs": [
            india_ref,
            us_ref
        ]
    }


# ============================================================
# 11. FINAL RESULT
# ============================================================

policy_relevance = (
    policy_result[
        "policy_relevance"
    ].strip()
)

policy_refs = (
    policy_result[
        "policy_refs"
    ]
)


# ============================================================
# 12. DISPLAY FINLLM REVIEW
# ============================================================

print(
    "\n========== FINLLM COMPLIANCE REVIEW ==========\n"
)


print("SUMMARY:")
print(summary)


print(
    "\nTRANSACTION OBSERVATION:"
)
print(
    transaction_observation
)


print(
    "\nPOLICY RELEVANCE:"
)
print(
    policy_relevance
)


print(
    "\nRECOMMENDED ACTION:"
)
print(
    recommended_action
)


print(
    "\nPOLICY REFERENCES:"
)

for ref in policy_refs:

    print(
        f"[{ref}]"
    )


print(
    "\n========== SOURCE DETAILS ==========\n"
)

for reference in source_details:

    print(reference)


# ============================================================
# 13. CREATE COMPLIANCE REVIEW TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS compliance_reviews (

        case_id TEXT PRIMARY KEY,

        summary TEXT NOT NULL,

        transaction_observation TEXT NOT NULL,

        policy_relevance TEXT NOT NULL,

        recommended_action TEXT NOT NULL,

        policy_refs TEXT NOT NULL
    )
    """
)


# ============================================================
# 14. SAVE VERIFIED REVIEW
# ============================================================

cursor.execute(
    """
    INSERT OR REPLACE INTO compliance_reviews (

        case_id,

        summary,

        transaction_observation,

        policy_relevance,

        recommended_action,

        policy_refs
    )

    VALUES (?, ?, ?, ?, ?, ?)
    """,

    (
        case_id,

        summary,

        transaction_observation,

        policy_relevance,

        recommended_action,

        ",".join(
            policy_refs
        )
    )
)


connection.commit()


# ============================================================
# 15. VERIFY DATABASE SAVE
# ============================================================

cursor.execute(
    """
    SELECT
        case_id,
        policy_refs
    FROM compliance_reviews
    WHERE case_id = ?
    """,
    (case_id,)
)


saved_review = (
    cursor.fetchone()
)


if saved_review is None:

    connection.close()

    raise SystemExit(
        "Compliance review was not saved."
    )


print(
    "\n========== DATABASE VERIFICATION ==========\n"
)

print(
    "Saved case:",
    saved_review[0]
)

print(
    "Saved policy references:",
    saved_review[1]
)


# ============================================================
# 16. CLOSE DATABASE
# ============================================================

connection.close()


print(
    "\nVerified compliance review saved to SQLite."
)

print(
    "\nPhase 4.4 compliance-explanation test finished."
)