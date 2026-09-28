import re
import sys
from collections import Counter

import config
from llm import ask_llm
from detect import load, add_features, apply_rules, apply_ml

DATA_DIR = config.BASE_DIR / "data" / "transactions"

REASON_TEXT = {
    "REPEATED_NEAR_CTR_THRESHOLD": "cash deposit between $9,000 and $9,999, with 2 or more such deposits within 7 days",
    "NEAR_CTR_THRESHOLD": "cash deposit between $9,000 and $9,999",
    "LARGE_VS_HISTORY": "amount is at least 10x this customer's usual transaction",
    "NEW_RECIPIENT_LARGE": "first transfer to this recipient, at least 5x the usual amount",
    "NEW_RECIPIENT": "first transfer to this recipient",
    "HIGH_VELOCITY": "5 or more transactions within one hour",
    "DORMANT_REACTIVATION": "first activity after 30 or more days without transactions",
    "FOREIGN_DESTINATION": "sent outside the US",
    "NIGHT_ACTIVITY": "made between midnight and 6am",
    "ML_ANOMALY": "the anomaly model rated this transaction statistically unusual",
}

REQUIRED = ["SUMMARY:", "WHAT WAS FLAGGED:", "WHY IT IS UNUSUAL", "OPEN QUESTIONS", "Decision:"]

SYSTEM_PROMPT = """You are FinLLM, assisting a bank AML analyst. Write an alert summary using ONLY the facts provided.
Rules:
1. Cite the transaction ID (e.g. T04800) for every statement about activity.
2. Use only amounts, dates and counts that appear in the facts. Do not count, add up or calculate anything yourself; use the counts given.
3. Describe what is unusual for this customer. Do NOT say the customer committed fraud, money laundering or any crime, and do not guess motives.
4. If a transaction's only reason is ML_ANOMALY, say the model found it statistically unusual and point to the metrics that stand out.
Format exactly:
SUMMARY: one or two sentences.
WHAT WAS FLAGGED:
- bullets, each with transaction IDs
WHY IT IS UNUSUAL FOR THIS CUSTOMER:
- bullets
OPEN QUESTIONS FOR THE ANALYST:
- two or three bullets
Decision: requires analyst review."""

JUDGMENTAL = ["money laundering", "laundering", "fraud", "criminal", "illegal", "guilty"]


def money(x):
    return f"${x:,.2f}"


def run_detection():
    df = apply_ml(apply_rules(add_features(load())))
    df["flagged"] = df["rule_flag"] | df["ml_flag"]
    df["risk_score"] = 3 * df["n_strong"] + df["n_weak"] + 2 * df["ml_flag"].astype(int)
    return df


def customer_facts(df, cid):
    """Fact sheet for Qwen. Every number, count and date range is computed here in Python."""
    hist = df[df.customer_id == cid]
    flagged = hist[hist.flagged]
    baseline = hist[~hist.flagged] if (~hist.flagged).any() else hist
    usual = baseline.amount.median()
    reason_counts = Counter(r for reasons in flagged.reasons for r in reasons)

    lines = [
        f"CUSTOMER: {cid}",
        f"History: {len(hist)} transactions from {hist.timestamp.min():%Y-%m-%d} to {hist.timestamp.max():%Y-%m-%d}",
        f"Usual (median) transaction amount: {money(usual)}",
        f"Countries used: {', '.join(sorted(hist.country.unique()))}",
        f"Flagged transactions: {len(flagged)}, total flagged amount {money(flagged.amount.sum())}",
        f"Flagged period: {flagged.timestamp.min():%Y-%m-%d %H:%M} to {flagged.timestamp.max():%Y-%m-%d %H:%M}",
        "Reason counts across flagged transactions: "
        + ", ".join(f"{r}: {n}" for r, n in reason_counts.most_common()),
        "",
        "FLAGGED TRANSACTIONS:",
    ]
    for _, t in flagged.iterrows():
        lines.append(
            f"- {t.txn_id} | {t.timestamp:%Y-%m-%d %H:%M} | {t.type} | {money(t.amount)} | to {t.recipient_id} | "
            f"{t.country} | {t.amount_ratio:.1f}x usual | {int(t.tx_last_hour)} txns in last hour | "
            f"{t.days_since_last:.0f} days since previous txn | {int(t.big_out_7d)} large outgoing in last 7 days")
        lines.append("  Reasons: " + "; ".join(f"{r} ({REASON_TEXT.get(r, r)})" for r in t.reasons))

    allowed_ids = set(flagged.txn_id)
    allowed_amounts = {round(a, 2) for a in flagged.amount}
    allowed_amounts |= {round(flagged.amount.sum(), 2), round(usual, 2), 9000.0, 9999.0, 10000.0}
    return "\n".join(lines), allowed_ids, allowed_amounts


def missing_sections(answer):
    return [s for s in REQUIRED if s.lower() not in answer.lower()]


def grounding_check(answer, allowed_ids, allowed_amounts):
    warnings = []
    bad_ids = sorted(set(re.findall(r"T\d{5}", answer)) - allowed_ids)
    if bad_ids:
        warnings.append(f"mentions transaction IDs not in the facts: {bad_ids}")
    for amt in re.findall(r"\$\d[\d,]*(?:\.\d+)?", answer):
        value = round(float(amt.replace("$", "").replace(",", "")), 2)
        if value not in allowed_amounts:
            warnings.append(f"amount {amt} not found in the facts (invented or rounded)")
    for word in JUDGMENTAL:
        if word in answer.lower():
            warnings.append(f"uses judgmental term '{word}'")
    return warnings


def main():
    df = run_detection()
    ranked = df[df.flagged].groupby("customer_id")["risk_score"].sum().sort_values(ascending=False)
    customers = [sys.argv[1]] if len(sys.argv) > 1 else list(ranked.index[:3])

    report = []
    for cid in customers:
        if cid not in ranked.index:
            print(f"{cid} has no flagged transactions.")
            continue
        facts, ids, amounts = customer_facts(df, cid)
        print(f"\n{'=' * 70}\n{cid}  (total risk score {ranked[cid]}) - writing summary...\n")

        answer = ask_llm(facts, system=SYSTEM_PROMPT)
        attempts = 1
        if missing_sections(answer):          # one retry with a firmer instruction
            answer = ask_llm(facts + "\n\nIMPORTANT: your answer MUST contain these headings exactly: "
                             + ", ".join(REQUIRED), system=SYSTEM_PROMPT)
            attempts = 2

        warnings = grounding_check(answer, ids, amounts)
        missing = missing_sections(answer)
        if missing:
            warnings.append(f"missing sections after {attempts} attempts: {missing}")

        print(answer)
        print(f"\nCHECKS (attempts: {attempts}):", "passed" if not warnings else "")
        for w in warnings:
            print(f"  WARN {w}")
        report.append(f"## {cid} (risk score {ranked[cid]})\n\n{answer}\n\n"
                      f"Checks: {'passed' if not warnings else '; '.join(warnings)}\n")

    name = sys.argv[1] if len(sys.argv) > 1 else "top3"
    out_file = DATA_DIR / f"explanations_{name}.md"
    out_file.write_text("\n".join(report))
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
