## C014 (risk score 75)

FLAGGED TRANSACTIONS (system data)
- T04531 | 2026-08-17 02:02 | transfer | $251.71 | to N4146 | US | NEW_RECIPIENT; NIGHT_ACTIVITY
- T04532 | 2026-08-17 02:07 | transfer | $269.58 | to N1172 | US | NEW_RECIPIENT; NIGHT_ACTIVITY
- T04533 | 2026-08-17 02:11 | transfer | $211.13 | to N7811 | US | NEW_RECIPIENT; NIGHT_ACTIVITY; ML_ANOMALY
- T04534 | 2026-08-17 02:14 | transfer | $332.93 | to N7301 | US | NEW_RECIPIENT; NIGHT_ACTIVITY; ML_ANOMALY
- T04535 | 2026-08-17 02:19 | transfer | $239.69 | to N1534 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04536 | 2026-08-17 02:21 | transfer | $185.23 | to N4565 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04537 | 2026-08-17 02:23 | transfer | $332.24 | to N7696 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04538 | 2026-08-17 02:26 | transfer | $233.77 | to N5370 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04539 | 2026-08-17 02:31 | transfer | $324.60 | to N5362 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04540 | 2026-08-17 02:34 | transfer | $344.13 | to N3057 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04541 | 2026-08-17 02:37 | transfer | $228.27 | to N7738 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04542 | 2026-08-17 02:42 | transfer | $208.68 | to N9501 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04543 | 2026-08-17 02:47 | transfer | $291.99 | to N1769 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY:  
A sequence of 13 flagged transactions occurred between 02:02 and 02:47 on 2026-08-17, all involving transfers to new recipients and occurring during nighttime hours. The transactions show a consistent pattern of increasing volume and amount over time, with the model identifying several as statistically unusual.

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- All flagged transactions occurred between midnight and 6am, a period with zero prior non-flagged transactions during the same time.  
- Every transaction involved a new recipient, indicating a pattern of unverified or unfamiliar counterparties.  
- The transaction volume increased steadily from 1 to 13 transactions within one hour, with a sustained high-velocity pattern (5+ transactions per hour) across all transactions.  
- The model flagged 11 of the 13 transactions as statistically unusual (ML_ANOMALY), highlighting deviations in amount, timing, or pattern beyond simple thresholds.

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer’s typical activity pattern during nighttime hours, and is there a known reason for such activity?  
- Are any of the recipient accounts linked to known high-risk or sanctioned entities?  
- Could the sequence of transactions be part of a coordinated or automated process, such as a test or bulk transfer?

Decision: requires analyst review.

Checks: passed

## C006 (risk score 61)

FLAGGED TRANSACTIONS (system data)
- T04668 | 2026-08-19 02:04 | transfer | $269.09 | to N5723 | US | NEW_RECIPIENT; NIGHT_ACTIVITY
- T04669 | 2026-08-19 02:09 | transfer | $276.05 | to N4617 | US | NEW_RECIPIENT; NIGHT_ACTIVITY
- T04670 | 2026-08-19 02:12 | transfer | $333.63 | to N6151 | US | NEW_RECIPIENT; NIGHT_ACTIVITY; ML_ANOMALY
- T04671 | 2026-08-19 02:16 | transfer | $276.19 | to N6146 | US | NEW_RECIPIENT; NIGHT_ACTIVITY; ML_ANOMALY
- T04672 | 2026-08-19 02:20 | transfer | $239.09 | to N4233 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04673 | 2026-08-19 02:23 | transfer | $211.92 | to N5501 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04674 | 2026-08-19 02:28 | transfer | $295.23 | to N8347 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04675 | 2026-08-19 02:33 | transfer | $233.51 | to N1907 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04676 | 2026-08-19 02:38 | transfer | $240.57 | to N8667 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04677 | 2026-08-19 02:41 | transfer | $347.53 | to N7910 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY
- T04678 | 2026-08-19 02:45 | transfer | $342.71 | to N4831 | US | NEW_RECIPIENT; HIGH_VELOCITY; NIGHT_ACTIVITY; ML_ANOMALY

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Eleven flagged transactions occurred between 02:04 and 02:45 on 2026-08-19, all within a one-hour window, involving multiple new recipients and significantly exceeding the customer’s usual transaction amount.  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- All flagged transactions occurred between midnight and 6am, a period with zero non-flagged transactions in the customer’s history.  
- Every transaction involved a new recipient, indicating no prior relationship with any of the recipients.  
- The transaction amounts ranged from 2.0x to 3.2x the customer’s usual amount of $101.62, with the highest being 3.2x.  
- The model identified ML_ANOMALY for nine of the eleven transactions, indicating statistically unusual behavior beyond the defined thresholds.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context or purpose behind the customer making multiple transfers to new recipients during a night-time window with no prior activity?  
- Are there any known relationships or accounts linked to the recipient IDs (N5723, N4617, etc.) that could explain the activity?  
- Could the high velocity of transactions (11 in one hour) be a result of a legitimate event, such as a bulk payout or automated process, or is it indicative of a pattern requiring further investigation?  

Decision: requires analyst review.

Checks: passed

## C015 (risk score 30)

FLAGGED TRANSACTIONS (system data)
- T03612 | 2026-08-01 15:47 | deposit | $9,528.43 | to SELF | US | NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03671 | 2026-08-02 15:17 | deposit | $9,282.83 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03699 | 2026-08-03 09:22 | deposit | $9,531.97 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03812 | 2026-08-04 17:58 | deposit | $9,286.45 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Four flagged deposits to self occurred between 2026-08-01 and 2026-08-04, each exceeding 45x the customer’s usual transaction amount. All transactions were cash deposits between $9,000 and $9,999, with multiple instances of repeated deposits within a 7-day window.

WHY IT IS UNUSUAL FOR THIS CUSTOMER:
- Each flagged transaction is at least 45x the customer’s usual transaction amount of $205.24, significantly exceeding historical norms.
- All four transactions are cash deposits between $9,000 and $9,999, triggering the NEAR_CTR_THRESHOLD rule, with at least two such deposits occurring within 7 days.
- The REPEATED_NEAR_CTR_THRESHOLD rule is triggered three times, indicating a pattern of multiple high-value deposits in a short period.
- The ML_ANOMALY flag is applied to all four transactions, indicating the model identified statistical deviations in amount, timing, or behavior.

OPEN QUESTIONS FOR THE ANALYST:
- What is the customer’s typical transaction pattern before 2026-08-01, and is there a known reason for large deposits in the past?
- Are there any known relationships or accounts linked to this customer that might explain the deposits to self?
- Could the deposits be part of a legitimate process (e.g., fund transfer, settlement) that has not been previously documented?

Decision: requires analyst review.

Checks: passed
