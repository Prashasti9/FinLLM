import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

import config

DATA_DIR = config.BASE_DIR / "data" / "transactions"

STRONG = {"REPEATED_NEAR_CTR_THRESHOLD", "LARGE_VS_HISTORY", "NEW_RECIPIENT_LARGE",
          "HIGH_VELOCITY", "DORMANT_REACTIVATION"}
WEAK = {"NEAR_CTR_THRESHOLD", "NEW_RECIPIENT", "FOREIGN_DESTINATION", "NIGHT_ACTIVITY"}


def load():
    df = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["timestamp"])
    df = df.drop(columns=["pattern"])    # the answer key — the detector must never see it
    return df.sort_values("timestamp").reset_index(drop=True)


def count_in_window(times, window):
    """For each event, how many of this customer's events fall in (t - window, t], including itself."""
    t = times.values
    return np.arange(1, len(t) + 1) - np.searchsorted(t, t - window, side="right")


def add_features(df):
    g = df.groupby("customer_id")

    df["prior_median"] = g["amount"].transform(lambda s: s.shift().expanding().median())
    df["amount_ratio"] = (df["amount"] / df["prior_median"]).fillna(1.0)
    df["days_since_last"] = g["timestamp"].diff().dt.total_seconds().div(86400).fillna(0)
    df["new_recipient"] = df["type"].eq("transfer") & (
        df.groupby(["customer_id", "recipient_id"]).cumcount() == 0)

    # NEW: outgoing payment/transfer at least 3x this customer's usual size
    df["big_outgoing"] = df["type"].isin(["payment", "transfer"]) & (df["amount_ratio"] >= 3)

    df["foreign"] = df["country"].ne("US")
    df["hour"] = df["timestamp"].dt.hour
    df["near_threshold"] = df["type"].eq("deposit") & df["amount"].between(9000, 9999.99)

    df["tx_last_hour"] = 0
    df["near_threshold_7d"] = 0
    df["big_out_7d"] = 0                    # NEW: how many big outgoing in the last 7 days
    for _, idx in g.groups.items():
        df.loc[idx, "tx_last_hour"] = count_in_window(df.loc[idx, "timestamp"], np.timedelta64(60, "m"))
        nt = df.loc[idx][df.loc[idx, "near_threshold"]]
        if len(nt):
            df.loc[nt.index, "near_threshold_7d"] = count_in_window(nt["timestamp"], np.timedelta64(7, "D"))
        bo = df.loc[idx][df.loc[idx, "big_outgoing"]]
        if len(bo):
            df.loc[bo.index, "big_out_7d"] = count_in_window(bo["timestamp"], np.timedelta64(7, "D"))
    return df


def apply_rules(df):
    reasons = [[] for _ in range(len(df))]

    def tag(mask, code):
        for i in np.flatnonzero(mask.values):
            reasons[i].append(code)

    tag(df["near_threshold"] & (df["near_threshold_7d"] >= 2), "REPEATED_NEAR_CTR_THRESHOLD")
    tag(df["near_threshold"] & (df["near_threshold_7d"] < 2), "NEAR_CTR_THRESHOLD")
    tag(df["amount_ratio"] >= 10, "LARGE_VS_HISTORY")
    tag(df["new_recipient"] & (df["amount_ratio"] >= 5), "NEW_RECIPIENT_LARGE")
    tag(df["new_recipient"] & (df["amount_ratio"] < 5), "NEW_RECIPIENT")
    tag(df["tx_last_hour"] >= 5, "HIGH_VELOCITY")
    tag(df["days_since_last"] >= 30, "DORMANT_REACTIVATION")
    tag(df["foreign"], "FOREIGN_DESTINATION")
    tag(df["hour"] < 6, "NIGHT_ACTIVITY")

    df["reasons"] = reasons
    df["n_strong"] = df["reasons"].apply(lambda r: sum(x in STRONG for x in r))
    df["n_weak"] = df["reasons"].apply(lambda r: sum(x in WEAK for x in r))
    df["rule_flag"] = (df["n_strong"] >= 1) | (df["n_weak"] >= 2)
    return df


def apply_ml(df):
    features = pd.DataFrame({
        "log_amount": np.log1p(df["amount"]),
        "log_ratio": np.log(df["amount_ratio"].clip(lower=1e-3)),
        "tx_last_hour": df["tx_last_hour"],
        "days_since_last": df["days_since_last"],
        "night": (df["hour"] < 6).astype(int),
        "big_out_7d": df["big_out_7d"],      # NEW behavioural feature
    })
    model = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
    df["ml_flag"] = model.fit_predict(features) == -1
    df["reasons"] = [r + ["ML_ANOMALY"] if m else r for r, m in zip(df["reasons"], df["ml_flag"])]
    return df


def main():
    df = apply_ml(apply_rules(add_features(load())))

    df["flagged"] = df["rule_flag"] | df["ml_flag"]
    df["source"] = np.select(
        [df["rule_flag"] & df["ml_flag"], df["rule_flag"], df["ml_flag"]],
        ["rules+ml", "rules", "ml"], default="")
    df["risk_score"] = 3 * df["n_strong"] + df["n_weak"] + 2 * df["ml_flag"].astype(int)
    df["reasons_text"] = df["reasons"].apply("; ".join)

    flags = df[df["flagged"]].sort_values("risk_score", ascending=False)
    cols = ["txn_id", "timestamp", "customer_id", "type", "amount", "recipient_id",
            "country", "risk_score", "source", "reasons_text"]
    flags[cols].to_csv(DATA_DIR / "flags.csv", index=False)

    print(f"Transactions analysed: {len(df)}")
    print(f"Flagged:               {len(flags)}  "
          f"(rules only {sum(flags.source == 'rules')}, ML only {sum(flags.source == 'ml')}, "
          f"both {sum(flags.source == 'rules+ml')})")
    print(f"Saved to {DATA_DIR / 'flags.csv'}\n")
    print("Top 10 by risk score:")
    print(flags[["txn_id", "customer_id", "type", "amount", "country",
                 "risk_score", "reasons_text"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
