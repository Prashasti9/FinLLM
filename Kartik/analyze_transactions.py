import pandas as pd

# ==========================================
# 1. LOAD TRANSACTION DATA
# ==========================================

FILE_PATH = "data/transactions/transactions.csv"

print("\nLoading transaction data...\n")

df = pd.read_csv(FILE_PATH)

print(f"Transactions loaded: {len(df)}")
print(f"Customers found: {df['customer_id'].nunique()}")

# ==========================================
# 2. VALIDATE REQUIRED COLUMNS
# ==========================================

required_columns = [
    "transaction_id",
    "customer_id",
    "timestamp",
    "amount",
    "transaction_type",
    "country",
    "beneficiary_id",
    "device_id",
    "channel"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise SystemExit(
        f"Missing required columns: {missing_columns}"
    )

print("Required columns: OK")

# ==========================================
# 3. CLEAN AND VALIDATE DATA
# ==========================================

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

if df["timestamp"].isna().any():
    raise SystemExit(
        "Invalid timestamp found."
    )

if df["amount"].isna().any():
    raise SystemExit(
        "Invalid transaction amount found."
    )

if (df["amount"] < 0).any():
    raise SystemExit(
        "Negative transaction amount found."
    )

if df["transaction_id"].duplicated().any():
    raise SystemExit(
        "Duplicate transaction IDs found."
    )

print("Data validation: PASSED")

# ==========================================
# 4. CUSTOMER STATISTICS
# ==========================================

customer_stats = (
    df.groupby("customer_id")["amount"]
    .agg(
        transaction_count="count",
        total_amount="sum",
        average_amount="mean",
        minimum_amount="min",
        maximum_amount="max"
    )
    .reset_index()
)

print("\n========== CUSTOMER STATISTICS ==========\n")

print(
    customer_stats.to_string(
        index=False
    )
)

# ==========================================
# 5. CALCULATE CUSTOMER BASELINE
# ==========================================

customer_sum = df.groupby(
    "customer_id"
)["amount"].transform("sum")

customer_count = df.groupby(
    "customer_id"
)["amount"].transform("count")

# Average of the customer's OTHER transactions.
# This prevents the current transaction from
# distorting its own baseline.

df["baseline_average"] = (
    (customer_sum - df["amount"])
    / (customer_count - 1)
)

df["amount_vs_baseline"] = (
    df["amount"]
    / df["baseline_average"]
)

# ==========================================
# 6. SHOW TRANSACTION ANALYSIS
# ==========================================

print("\n========== TRANSACTION ANALYSIS ==========\n")

display_columns = [
    "transaction_id",
    "customer_id",
    "amount",
    "baseline_average",
    "amount_vs_baseline",
    "country",
    "device_id"
]

print(
    df[display_columns]
    .round(
        {
            "amount": 2,
            "baseline_average": 2,
            "amount_vs_baseline": 2
        }
    )
    .to_string(index=False)
)

# ==========================================
# 7. SAVE ANALYSIS
# ==========================================

OUTPUT_PATH = (
    "data/transactions/"
    "transaction_analysis.csv"
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"\nAnalysis saved to: {OUTPUT_PATH}"
)

print("\nPhase 3 transaction analysis test finished.")