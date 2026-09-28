import subprocess
import sys

import pandas as pd

import config
from detect import load, add_features, apply_rules, apply_ml

DATA_DIR = config.BASE_DIR / "data" / "transactions"
SEEDS = [1, 2, 3, 4, 5]   # datasets never used while tuning (tuning used seed 42)


def score_current_dataset():
    df = apply_ml(apply_rules(add_features(load())))      # detector never sees the answer key
    df["flagged"] = df["rule_flag"] | df["ml_flag"]
    truth = pd.read_csv(DATA_DIR / "transactions.csv")[["txn_id", "pattern"]]
    df = df.merge(truth, on="txn_id")

    susp = df["pattern"].ne("normal")
    tp = (df.flagged & susp).sum()
    fp = (df.flagged & ~susp).sum()
    fn = (~df.flagged & susp).sum()
    susp_c = set(df.loc[susp, "customer_id"])
    caught_c = set(df.loc[susp & df.flagged, "customer_id"])
    innocent_c = set(df.loc[df.flagged, "customer_id"]) - susp_c
    spree = df[df["pattern"] == "spending_spree"]

    return {
        "precision": tp / max(tp + fp, 1),
        "recall": tp / max(tp + fn, 1),
        "customers_caught": f"{len(caught_c)}/{len(susp_c)}",
        "innocent_flagged": len(innocent_c),
        "spree_recall": spree["flagged"].mean() if len(spree) else float("nan"),
    }


def main():
    rows = []
    for seed in SEEDS:
        subprocess.run([sys.executable, "generate_transactions.py", str(seed)], check=True, capture_output=True)
        result = score_current_dataset()
        result["seed"] = seed
        rows.append(result)
        print(f"seed {seed}: precision {result['precision']:.0%}  recall {result['recall']:.0%}  "
              f"customers {result['customers_caught']}  innocent flagged {result['innocent_flagged']}  "
              f"spree {result['spree_recall']:.0%}")

    table = pd.DataFrame(rows)
    print("\n=== ACROSS 5 UNSEEN DATASETS ===")
    for col in ["precision", "recall", "spree_recall"]:
        print(f"{col:<13} mean {table[col].mean():.0%}   std {table[col].std():.0%}   "
              f"range {table[col].min():.0%} to {table[col].max():.0%}")
    print(f"innocent customers flagged: mean {table['innocent_flagged'].mean():.1f}")

    # Put back the original dataset (seed 42) so flags and narratives stay consistent
    subprocess.run([sys.executable, "generate_transactions.py"], check=True, capture_output=True)
    subprocess.run([sys.executable, "detect.py"], check=True, capture_output=True)
    print("\nRestored the seed-42 dataset and flags.csv.")


if __name__ == "__main__":
    main()
