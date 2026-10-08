import sqlite3
import re

DB_FILE = "data/database/finllm.db"

print("\nConnecting to FinLLM financial database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

question = input("\nAsk Financial FinLLM: ").strip()

if not question:
    connection.close()
    raise SystemExit("Please enter a question.")

question_lower = question.lower()

print("\n========== FINANCIAL RESULT ==========\n")


# ==================================================
# QUERY 1 — HIGHEST DEVIATION TRANSACTION
# ==================================================

if (
    "deviat" in question_lower
    or "unusual" in question_lower
    or "highest" in question_lower
):

    query = """
    SELECT
        transaction_id,
        customer_id,
        amount,
        baseline_average,
        amount_vs_baseline,
        country,
        device_id
    FROM transaction_analysis
    ORDER BY amount_vs_baseline DESC
    LIMIT 1
    """

    cursor.execute(query)
    row = cursor.fetchone()

    if row:
        print("Highest-deviation transaction")
        print("Transaction:", row[0])
        print("Customer:", row[1])
        print("Amount:", round(row[2], 2))
        print("Baseline:", round(row[3], 2))
        print("Deviation ratio:", round(row[4], 2))
        print("Country:", row[5])
        print("Device:", row[6])


# ==================================================
# QUERY 2 — CUSTOMER SUMMARY
# ==================================================

elif "customer" in question_lower:

    match = re.search(
        r"\bC\d+\b",
        question,
        re.IGNORECASE
    )

    if not match:
        print(
            "Please include a customer ID, "
            "for example C001."
        )

    else:
        customer_id = match.group().upper()

        query = """
        SELECT
            customer_id,
            transaction_count,
            total_amount,
            average_amount,
            minimum_amount,
            maximum_amount
        FROM customer_summary
        WHERE customer_id = ?
        """

        cursor.execute(
            query,
            (customer_id,)
        )

        row = cursor.fetchone()

        if row:
            print("Customer:", row[0])
            print("Transaction count:", row[1])
            print("Total amount:", round(row[2], 2))
            print("Average amount:", round(row[3], 2))
            print("Minimum amount:", round(row[4], 2))
            print("Maximum amount:", round(row[5], 2))

        else:
            print(
                f"No customer found with ID {customer_id}."
            )


# ==================================================
# QUERY 3 — TRANSACTION DETAILS
# ==================================================

elif "transaction" in question_lower:

    match = re.search(
        r"\bTX\d+\b",
        question,
        re.IGNORECASE
    )

    if not match:
        print(
            "Please include a transaction ID, "
            "for example TX1005."
        )

    else:
        transaction_id = match.group().upper()

        query = """
        SELECT
            transaction_id,
            customer_id,
            amount,
            baseline_average,
            amount_vs_baseline,
            country,
            device_id
        FROM transaction_analysis
        WHERE transaction_id = ?
        """

        cursor.execute(
            query,
            (transaction_id,)
        )

        row = cursor.fetchone()

        if row:
            print("Transaction:", row[0])
            print("Customer:", row[1])
            print("Amount:", round(row[2], 2))
            print("Baseline:", round(row[3], 2))
            print("Deviation ratio:", round(row[4], 2))
            print("Country:", row[5])
            print("Device:", row[6])

        else:
            print(
                f"No transaction found with ID "
                f"{transaction_id}."
            )


# ==================================================
# UNSUPPORTED QUESTION
# ==================================================

else:
    print(
        "This financial question is not supported "
        "by the current deterministic query layer."
    )

connection.close()

print("\nFinancial query test finished.")