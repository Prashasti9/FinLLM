import pandas as pd
import sqlite3

ANALYSIS_FILE = "data/transactions/transaction_analysis.csv"
DB_FILE = "data/database/finllm.db"
OUTPUT_FILE = "data/transactions/risk_scores.csv"

print("\nLoading analyzed transaction data...")

df = pd.read_csv(ANALYSIS_FILE)

print(f"Transactions loaded: {len(df)}")


# ==================================================
# 1. PREPARE RISK COLUMNS
# ==================================================

df["risk_score"] = 0
df["risk_reasons"] = ""


# ==================================================
# 2. BEHAVIORAL RISK RULES
# ==================================================

for index, row in df.iterrows():

    score = 0
    reasons = []

    customer_id = row["customer_id"]
    transaction_id = row["transaction_id"]
    deviation = row["amount_vs_baseline"]

    # Other transactions belonging to this customer
    history = df[
        (df["customer_id"] == customer_id)
        & (df["transaction_id"] != transaction_id)
    ]


    # ----------------------------------------------
    # RULE 1 — TRANSACTION AMOUNT DEVIATION
    # ----------------------------------------------

    if pd.notna(deviation):

        if deviation >= 10:
            score += 60
            reasons.append(
                f"Amount is {deviation:.2f}x customer baseline"
            )

        elif deviation >= 3:
            score += 40
            reasons.append(
                f"Amount is {deviation:.2f}x customer baseline"
            )

        elif deviation >= 2:
            score += 20
            reasons.append(
                f"Amount is {deviation:.2f}x customer baseline"
            )


    # ----------------------------------------------
    # RULE 2 — COUNTRY NOT SEEN IN OTHER HISTORY
    # ----------------------------------------------

    if not history.empty:

        historical_countries = set(
            history["country"]
            .dropna()
            .astype(str)
        )

        current_country = str(row["country"])

        if (
            historical_countries
            and current_country not in historical_countries
        ):
            score += 20
            reasons.append(
                "Country not seen in customer's other transactions"
            )


    # ----------------------------------------------
    # RULE 3 — DEVICE NOT SEEN IN OTHER HISTORY
    # ----------------------------------------------

    if not history.empty:

        historical_devices = set(
            history["device_id"]
            .dropna()
            .astype(str)
        )

        current_device = str(row["device_id"])

        if (
            historical_devices
            and current_device not in historical_devices
        ):
            score += 20
            reasons.append(
                "Device not seen in customer's other transactions"
            )


    # ----------------------------------------------
    # STORE RESULT
    # ----------------------------------------------

    score = min(score, 100)

    df.at[index, "risk_score"] = score

    if reasons:
        df.at[index, "risk_reasons"] = "; ".join(reasons)
    else:
        df.at[index, "risk_reasons"] = (
            "No current behavioral rules triggered"
        )


# ==================================================
# 3. ASSIGN REVIEW LEVEL
# ==================================================

def review_level(score):

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


df["review_level"] = df["risk_score"].apply(review_level)


# ==================================================
# 4. DISPLAY RESULTS
# ==================================================

print("\n========== TRANSACTION RISK RESULTS ==========\n")

display_columns = [
    "transaction_id",
    "customer_id",
    "amount",
    "amount_vs_baseline",
    "risk_score",
    "review_level",
    "risk_reasons"
]

print(
    df[display_columns]
    .sort_values(
        "risk_score",
        ascending=False
    )
    .to_string(index=False)
)


# ==================================================
# 5. SAVE TO CSV
# ==================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nRisk results saved to: {OUTPUT_FILE}"
)


# ==================================================
# 6. SAVE TO SQLITE
# ==================================================

connection = sqlite3.connect(DB_FILE)

risk_table = df[
    [
        "transaction_id",
        "customer_id",
        "risk_score",
        "review_level",
        "risk_reasons"
    ]
]

risk_table.to_sql(
    "risk_scores",
    connection,
    if_exists="replace",
    index=False
)

connection.commit()
connection.close()

print("SQLite table created: risk_scores")

print("\nPhase 4.1 risk-engine test finished.")