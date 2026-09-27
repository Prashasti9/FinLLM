import pandas as pd
import config

DATA_DIR = config.BASE_DIR / "data" / "transactions"

tx = pd.read_csv(DATA_DIR / "transactions.csv")      # includes the answer key
flags = pd.read_csv(DATA_DIR / "flags.csv")

tx["flagged"] = tx["txn_id"].isin(flags["txn_id"])
tx["suspicious"] = tx["pattern"].ne("normal")

tp = (tx.flagged & tx.suspicious).sum()
fp = (tx.flagged & ~tx.suspicious).sum()
fn = (~tx.flagged & tx.suspicious).sum()

print("=== TRANSACTION LEVEL ===")
print(f"Caught (true positives):   {tp}")
print(f"False alarms:              {fp}")
print(f"Missed:                    {fn}")
print(f"Precision: {tp / max(tp + fp, 1):.0%}  (of flags raised, how many were real)")
print(f"Recall:    {tp / max(tp + fn, 1):.0%}  (of real cases, how many we caught)\n")

print("Recall by pattern:")
for pattern, group in tx[tx.suspicious].groupby("pattern"):
    print(f"  {pattern:<18} {group.flagged.sum()}/{len(group)}")

susp_c = set(tx.loc[tx.suspicious, "customer_id"])
flag_c = set(tx.loc[tx.flagged, "customer_id"])
caught_c = set(tx.loc[tx.suspicious & tx.flagged, "customer_id"])   # caught via a REAL suspicious txn

print("\n=== CUSTOMER LEVEL (what an investigator cares about) ===")
print(f"Suspicious customers caught: {len(caught_c)}/{len(susp_c)}")
print(f"Missed customers:            {sorted(susp_c - caught_c) or 'none'}")
print(f"Innocent customers flagged:  {len(flag_c - susp_c)}  {sorted(flag_c - susp_c)}")

false_alarms = flags.merge(tx[["txn_id", "pattern"]], on="txn_id").query("pattern == 'normal'")
if len(false_alarms):
    print("\nSample false alarms (why were these flagged?):")
    print(false_alarms[["txn_id", "customer_id", "type", "amount", "source",
                        "reasons_text"]].head(10).to_string(index=False))

merged = tx.merge(flags[["txn_id", "source"]], on="txn_id", how="left")
print("\nWho caught each pattern (rules / ml / rules+ml / missed):")
for pattern, group in merged[merged.suspicious].groupby("pattern"):
    print(f"  {pattern:<18} {group['source'].fillna('missed').value_counts().to_dict()}")
