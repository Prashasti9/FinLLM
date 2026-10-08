import json
import sqlite3
import ollama

DB_FILE = "data/database/finllm.db"

# ==========================================
# 1. CONNECT TO SQLITE
# ==========================================

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

# ==========================================
# 2. DETERMINISTIC SQL QUERY
# ==========================================

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

if row is None:
    raise SystemExit("No transaction data found.")

(
    transaction_id,
    customer_id,
    amount,
    baseline_average,
    amount_vs_baseline,
    country,
    device_id
) = row

print("\n========== SQL RESULT ==========\n")

print("Transaction:", transaction_id)
print("Customer:", customer_id)
print("Amount:", amount)
print("Baseline average:", round(baseline_average, 2))
print("Deviation ratio:", round(amount_vs_baseline, 2))
print("Country:", country)
print("Device:", device_id)

# ==========================================
# 3. LET QWEN EXPLAIN THE RESULT
# ==========================================

evidence = f"""
Transaction ID: {transaction_id}
Customer ID: {customer_id}
Amount: ${amount:.2f}
Customer baseline average: ${baseline_average:.2f}
Amount vs baseline: {amount_vs_baseline:.2f}x
Country: {country}
Device ID: {device_id}
"""

print("\nGenerating FinLLM explanation...\n")


answer_schema = {
    "type": "object",
    "properties": {
        "explanation": {
            "type": "string"
        }
    },
    "required": ["explanation"],
    "additionalProperties": False
}

response = ollama.chat(
    model="qwen3:4b",
    think=False,
    stream=False,
    format=answer_schema,
    messages=[
        {
            "role": "system",
            "content": (
                "You are FinLLM, a financial analysis assistant. "
                "Use ONLY the supplied database evidence. "
                "Return only the final explanation. "
                "Do not show reasoning, analysis, or chain of thought. "
                "Do not use the words fraud, fraudulent, suspicious, "
                "money laundering, criminal, or illegal unless those facts "
                "are explicitly supplied in the evidence. "
                "Do not interpret or expand country codes. "
                "For example, if the evidence says AE, say AE, not UAE. "
                "Explain only how the transaction differs from the customer's "
                "calculated baseline. "
                "State that the deviation warrants further review but does not "
                "establish wrongdoing. "
                "Use no more than 3 sentences. "
                "Do not invent any facts."
            )
        },
        {
            "role": "user",
            "content": (
                "/no_think\n"
                "Explain this transaction using only this evidence:\n\n"
                + evidence
            )
        }
    ],
    options={
        "temperature": 0,
        "num_predict": 150
    }
)
result = json.loads(
    response["message"]["content"]
)

answer = result["explanation"]

print("========== FINLLM EXPLANATION ==========\n")
print(answer)

connection.close()

print("\nSQL + FinLLM test finished.")