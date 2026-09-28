## C020 (risk score 4)

FLAGGED TRANSACTIONS (system data)
- T00379 | 2026-06-07 15:11 | deposit | $1,399.54 | to SELF | US | ML_ANOMALY
- T00899 | 2026-06-16 12:37 | deposit | $1,111.63 | to SELF | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 2 of 2 were rated statistically unusual by the anomaly model; 2 for that reason alone, at 2.2x to 3.6x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Two deposits to self were flagged during a five-day period in June 2026, each exceeding the usual transaction amount by 2.2x to 3.6x, with no large outgoing transactions in the prior seven days. The model identified both as statistically unusual based on amount and frequency metrics.

OPEN QUESTIONS FOR THE ANALYST:
- What is the customer’s typical behavior regarding deposits to self, and is this pattern consistent with known activity?
- Are there any known account changes, such as new beneficiaries or account access, that could explain the deposits?
- Why did the anomaly model flag both transactions despite no outgoing activity or recent activity in the past seven days?

Decision: requires analyst review.

Checks: passed
