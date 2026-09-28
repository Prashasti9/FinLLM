import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import config

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 42)          # fixed seed = same data every run
START = datetime(2026, 6, 1)
DAYS = 90
N_CUSTOMERS = 50

OUT_DIR = config.BASE_DIR / "data" / "transactions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

rows = []


def add(customer, ts, ttype, amount, recipient, channel, country, pattern="normal"):
    rows.append({
        "timestamp": ts, "customer_id": customer, "type": ttype,
        "amount": round(float(amount), 2), "recipient_id": str(recipient),
        "channel": channel, "country": str(country), "pattern": pattern,
    })


def daytime(day):
    """A random time between 8am and 8pm on a given day."""
    return START + timedelta(days=int(day), hours=int(rng.integers(8, 20)),
                             minutes=int(rng.integers(0, 60)))


# ---------- Customer profiles ----------
customers = [f"C{i:03d}" for i in range(1, N_CUSTOMERS + 1)]
profiles = {
    c: {
        "typical": float(rng.lognormal(mean=5, sigma=0.6)),   # typical spend, roughly $50-$500
        "payees": [f"P{rng.integers(1000, 9999)}" for _ in range(int(rng.integers(2, 5)))],
    }
    for c in customers
}

# Pick 10 customers to carry suspicious patterns
special = [str(c) for c in rng.choice(customers, size=12, replace=False)]
structurers, big_new, bursters, dormant = special[:3], special[3:6], special[6:8], special[8:10]

# ---------- Normal activity ----------
for c in customers:
    p = profiles[c]
    active_days = range(0, 10) if c in dormant else range(0, DAYS)   # dormant: goes quiet after day 10
    for day in active_days:
        for _ in range(int(rng.poisson(1.2))):                        # ~1 transaction a day
            kind = str(rng.choice(["payment", "transfer", "deposit", "withdrawal"],
                                  p=[0.5, 0.2, 0.2, 0.1]))
            amount = rng.lognormal(np.log(p["typical"]), 0.4)
            if kind == "payment":
                recipient, channel = f"M{rng.integers(100, 999)}", "card"
            elif kind == "transfer":
                recipient, channel = rng.choice(p["payees"]), "online"
            elif kind == "deposit":
                recipient, channel, amount = "SELF", "branch", amount * 3
            else:
                recipient, channel = "SELF", "atm"
            add(c, daytime(day), kind, amount, recipient, channel, "US")

# ---------- Planted suspicious patterns ----------
# 1. Structuring: several cash deposits just under $10,000 on consecutive days
for c in structurers:
    d = int(rng.integers(60, 80))
    for k in range(int(rng.integers(4, 7))):
        add(c, daytime(d + k), "deposit", rng.uniform(9000, 9900), "SELF", "branch", "US", "structuring")

# 2. One very large transfer to a brand-new recipient abroad
for c in big_new:
    d = int(rng.integers(60, 88))
    add(c, daytime(d), "transfer", profiles[c]["typical"] * rng.uniform(40, 80),
        f"X{rng.integers(1000, 9999)}", "online", rng.choice(["AE", "KY", "PA", "CY"]), "large_new_foreign")

# 3. Velocity burst: 10-15 transfers to new recipients within ~1 hour, at 2am
for c in bursters:
    base = START + timedelta(days=int(rng.integers(60, 88)), hours=2)
    minutes = 0
    for k in range(int(rng.integers(10, 16))):
        minutes += int(rng.integers(2, 6))
        add(c, base + timedelta(minutes=minutes), "transfer", profiles[c]["typical"] * rng.uniform(2, 4),
            f"N{rng.integers(1000, 9999)}", "online", "US", "velocity_burst")

# 4. Dormant account suddenly moves large sums in and straight out
for c in dormant:
    d = int(rng.integers(82, 88))
    add(c, daytime(d), "deposit", rng.uniform(40000, 60000), "SELF", "wire", "US", "dormant_spike")
    add(c, daytime(d + 1), "transfer", rng.uniform(38000, 58000),
        f"X{rng.integers(1000, 9999)}", "online", "US", "dormant_spike")

# 5. NEW - no rule covers this: a spree of round-number card payments
#    daytime, domestic, a payment not a transfer, each under 10x usual -> invisible to our rules
spree = special[10:12]
for c in spree:
    d = int(rng.integers(55, 75))
    for k in range(int(rng.integers(8, 13))):
        amount = round(profiles[c]["typical"] * rng.uniform(5, 8) / 50) * 50
        add(c, daytime(d + k), "payment", amount, f"M{rng.integers(100, 999)}", "card", "US", "spending_spree")# ---------- Save ----------
df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
df.insert(0, "txn_id", [f"T{i:05d}" for i in range(1, len(df) + 1)])
df.to_csv(OUT_DIR / "transactions.csv", index=False)

print(f"Saved {len(df)} transactions to {OUT_DIR / 'transactions.csv'}")
print(f"Customers: {df['customer_id'].nunique()}   "
      f"Dates: {df['timestamp'].min():%Y-%m-%d} to {df['timestamp'].max():%Y-%m-%d}\n")
print("Transactions per pattern:")
print(df["pattern"].value_counts().to_string())
print("\nWho carries each pattern (the answer key):")
for name, group in [("structuring", structurers), ("large_new_foreign", big_new),
                    ("velocity_burst", bursters), ("dormant_spike", dormant)]:
    print(f"  {name:<18} {', '.join(group)}")
print(f"  {'spending_spree':<18} {', '.join(spree)}")
