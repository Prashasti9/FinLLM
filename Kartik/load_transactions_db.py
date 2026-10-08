import sqlite3
import pandas as pd

# ==========================================
# 1. FILE PATHS
# ==========================================

RAW_FILE = "data/transactions/transactions.csv"
ANALYSIS_FILE = "data/transactions/transaction_analysis.csv"
DB_FILE = "data/database/finllm.db"

# ==========================================
# 2. LOAD CSV DATA
# ==========================================

print("\nLoading transaction files...")

transactions = pd.read_csv(RAW_FILE)
analysis = pd.read_csv(ANALYSIS_FILE)

print(f"Raw transactions: {len(transactions)}")
print(f"Analyzed transactions: {len(analysis)}")

# ==========================================
# 3. CREATE CUSTOMER SUMMARY
# ==========================================

customer_summary = (
    transactions
    .groupby("customer_id")["amount"]
    .agg(
        transaction_count="count",
        total_amount="sum",
        average_amount="mean",
        minimum_amount="min",
        maximum_amount="max"
    )
    .reset_index()
)

# ==========================================
# 4. CONNECT TO SQLITE
# ==========================================

print("\nConnecting to SQLite...")

connection = sqlite3.connect(DB_FILE)

# ==========================================
# 5. SAVE TABLES
# ==========================================

transactions.to_sql(
    "transactions",
    connection,
    if_exists="replace",
    index=False
)

analysis.to_sql(
    "transaction_analysis",
    connection,
    if_exists="replace",
    index=False
)

customer_summary.to_sql(
    "customer_summary",
    connection,
    if_exists="replace",
    index=False
)

connection.commit()

print("SQLite tables created successfully.")

# ==========================================
# 6. VERIFY DATABASE
# ==========================================

cursor = connection.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""")

tables = cursor.fetchall()

print("\n========== DATABASE TABLES ==========\n")

for table in tables:
    print(table[0])

# ==========================================
# 7. TEST QUERY
# ==========================================

print("\n========== CUSTOMER SUMMARY ==========\n")

query = """
SELECT
    customer_id,
    transaction_count,
    ROUND(total_amount, 2),
    ROUND(average_amount, 2),
    ROUND(maximum_amount, 2)
FROM customer_summary
ORDER BY customer_id
"""

for row in cursor.execute(query):
    print(row)

# ==========================================
# 8. TEST LARGE-DEVIATION QUERY
# ==========================================

print("\n========== HIGH DEVIATION TRANSACTIONS ==========\n")

query = """
SELECT
    transaction_id,
    customer_id,
    amount,
    ROUND(baseline_average, 2),
    ROUND(amount_vs_baseline, 2)
FROM transaction_analysis
WHERE amount_vs_baseline >= 3
ORDER BY amount_vs_baseline DESC
"""

for row in cursor.execute(query):
    print(row)

connection.close()

print(f"\nDatabase saved to: {DB_FILE}")
print("\nSQLite integration test finished.")