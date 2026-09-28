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

WHY IT IS UNUSUAL (computed by the system)
- 13 of 13 went to a recipient this customer had never paid before.
- 9 of 13 were part of a burst of 5 or more transactions within one hour (up to 13 in one hour).
- 13 of 13 were made before 6am; 0 of the customer's 115 other transactions were.
- Up to 4 large outgoing payments (3x usual or more) were made within 7 days.
- 11 of 13 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: All 13 flagged transactions occurred before 6am, involved new recipients, and were part of a rapid burst of 5 or more transfers within one hour, with the anomaly model identifying 11 as statistically unusual.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer’s typical activity pattern before 6am, and is there a known reason for activity at this time?  
- Are any of the recipients linked to known high-risk or sanctioned entities?  
- What is the nature of the large outgoing payments in the last 7 days, and is there a pattern of cumulative volume or frequency?  

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

WHY IT IS UNUSUAL (computed by the system)
- 11 of 11 went to a recipient this customer had never paid before.
- 7 of 11 were part of a burst of 5 or more transactions within one hour (up to 11 in one hour).
- 11 of 11 were made before 6am; 0 of the customer's 117 other transactions were.
- Up to 3 large outgoing payments (3x usual or more) were made within 7 days.
- 9 of 11 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Eleven transactions to previously unknown recipients occurred between 02:04 and 02:45 on 2026-08-19, all before 6am, with a burst of five or more transactions within one hour, and nine rated statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the purpose or context of these transfers to new recipients?  
- Are there any known relationships or patterns linking these recipients to one another or to other accounts?  
- What is the customer’s typical activity pattern outside of this period, and why did this activity occur at such an unusual time?  

Decision: requires analyst review.

Checks: passed

## C015 (risk score 30)

FLAGGED TRANSACTIONS (system data)
- T03612 | 2026-08-01 15:47 | deposit | $9,528.43 | to SELF | US | NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03671 | 2026-08-02 15:17 | deposit | $9,282.83 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03699 | 2026-08-03 09:22 | deposit | $9,531.97 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03812 | 2026-08-04 17:58 | deposit | $9,286.45 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 4 of 4 flagged transactions were at least 10x the usual amount of $205.24 (highest: 47.1x).
- 4 of 4 were cash deposits between $9,000 and $9,999; 3 of these came with 2 or more such deposits within 7 days.
- 4 of 4 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Four flagged transactions occurred between 2026-08-01 and 2026-08-04, each involving a cash deposit between $9,000 and $9,999, at least 10x the customer’s usual transaction amount, and all were rated statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context or purpose of the customer making multiple large deposits to self within a short period?  
- Are there any known patterns or events in the customer’s history that might explain these transactions?  
- Could the repeated deposits be part of a coordinated activity, such as a cash flow management strategy or a different type of behavior?  

Decision: requires analyst review.

Checks: passed

## C049 (risk score 30)

FLAGGED TRANSACTIONS (system data)
- T03736 | 2026-08-03 15:02 | deposit | $9,398.02 | to SELF | US | NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03814 | 2026-08-04 18:22 | deposit | $9,491.17 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03892 | 2026-08-05 19:42 | deposit | $9,278.83 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T03924 | 2026-08-06 13:11 | deposit | $9,739.91 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 4 of 4 flagged transactions were at least 10x the usual amount of $205.05 (highest: 47.5x).
- 4 of 4 were cash deposits between $9,000 and $9,999; 3 of these came with 2 or more such deposits within 7 days.
- 4 of 4 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Four cash deposits to self between 2026-08-03 and 2026-08-06 were each at least 10x the customer’s usual transaction amount, with three involving repeated deposits within 7 days, and all were rated statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context or purpose behind the customer making multiple large deposits to self in a short period?  
- Are there any known account activity patterns or external events that could explain the timing or nature of these deposits?  
- Could the repeated deposits within 7 days reflect a pattern of behavior that warrants further investigation, even if no other transactions are flagged?  

Decision: requires analyst review.

Checks: passed

## C050 (risk score 30)

FLAGGED TRANSACTIONS (system data)
- T04717 | 2026-08-19 18:02 | deposit | $9,317.65 | to SELF | US | NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T04740 | 2026-08-20 10:13 | deposit | $9,119.58 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T04800 | 2026-08-21 12:09 | deposit | $9,743.64 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY
- T04868 | 2026-08-22 13:05 | deposit | $9,652.37 | to SELF | US | REPEATED_NEAR_CTR_THRESHOLD; LARGE_VS_HISTORY; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 4 of 4 flagged transactions were at least 10x the usual amount of $120.74 (highest: 78.1x).
- 4 of 4 were cash deposits between $9,000 and $9,999; 3 of these came with 2 or more such deposits within 7 days.
- 4 of 4 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Four cash deposits to self between 2026-08-19 and 2026-08-22 were each at least 10x the customer’s usual transaction amount, all within the $9,000 to $9,999 range, with three involving repeated deposits within 7 days, and all were rated statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer’s typical transaction pattern, and is there a known reason for large deposits to self?  
- Are there any other transactions or activity patterns (e.g., outgoing transfers, account balances) that could explain the large deposits?  
- Could the repeated deposits within 7 days be part of a coordinated pattern, even if not directly linked to a single event?  

Decision: requires analyst review.

Checks: passed

## C025 (risk score 16)

FLAGGED TRANSACTIONS (system data)
- T05221 | 2026-08-27 18:16 | deposit | $52,352.36 | to SELF | US | LARGE_VS_HISTORY; DORMANT_REACTIVATION; ML_ANOMALY
- T05284 | 2026-08-28 18:23 | transfer | $44,415.49 | to X8195 | US | LARGE_VS_HISTORY; NEW_RECIPIENT_LARGE; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 2 of 2 flagged transactions were at least 10x the usual amount of $68.19 (highest: 767.7x).
- 1 of 2 went to a recipient this customer had never paid before.
- 1 of 2 came after a gap of 79 days with no activity.
- 2 of 2 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Two large deposits and transfers occurred within a short period in August 2026, with amounts significantly exceeding the customer’s usual transaction size and one involving a new recipient. Both transactions were flagged for being statistically unusual by the anomaly model.

OPEN QUESTIONS FOR THE ANALYST:
- What is the context or purpose of the customer’s deposit to self on 2026-08-27?
- Why did the customer initiate a transfer to a new recipient shortly after reactivating activity?
- What is the significance of the 79-day gap before the first flagged transaction?

Decision: requires analyst review.

Checks: passed

## C032 (risk score 16)

FLAGGED TRANSACTIONS (system data)
- T05180 | 2026-08-27 10:10 | deposit | $47,782.23 | to SELF | US | LARGE_VS_HISTORY; DORMANT_REACTIVATION; ML_ANOMALY
- T05287 | 2026-08-28 18:52 | transfer | $54,742.02 | to X5912 | US | LARGE_VS_HISTORY; NEW_RECIPIENT_LARGE; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 2 of 2 flagged transactions were at least 10x the usual amount of $62.39 (highest: 872.9x).
- 1 of 2 went to a recipient this customer had never paid before.
- 1 of 2 came after a gap of 78 days with no activity.
- 2 of 2 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Two large deposits and transfers occurred within a short period, both significantly exceeding the customer’s usual transaction amount and involving a new recipient. The transactions were flagged for being unusually large, involving a new recipient, and showing a significant gap in activity.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context or purpose of the customer’s deposit to self and transfer to a new recipient?  
- Is there a pattern of activity in the 78-day gap that might explain the reactivation?  
- Why did both transactions trigger the ML_ANOMALY flag, and what specific metrics did the model identify as unusual?  

Decision: requires analyst review.

Checks: passed

## C037 (risk score 16)

FLAGGED TRANSACTIONS (system data)
- T03935 | 2026-08-06 16:58 | payment | $1,800.00 | to M944 | US | ML_ANOMALY
- T03971 | 2026-08-07 12:00 | payment | $1,850.00 | to M876 | US | ML_ANOMALY
- T04037 | 2026-08-08 13:42 | payment | $1,400.00 | to M418 | US | ML_ANOMALY
- T04114 | 2026-08-09 19:46 | payment | $1,750.00 | to M126 | US | ML_ANOMALY
- T04130 | 2026-08-10 10:46 | payment | $1,650.00 | to M195 | US | ML_ANOMALY
- T04219 | 2026-08-11 15:22 | payment | $1,250.00 | to M208 | US | ML_ANOMALY
- T04301 | 2026-08-12 19:29 | payment | $1,800.00 | to M395 | US | ML_ANOMALY
- T04347 | 2026-08-13 19:08 | payment | $1,550.00 | to M838 | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- Up to 7 large outgoing payments (3x usual or more) were made within 7 days.
- 8 of 8 were rated statistically unusual by the anomaly model; 8 for that reason alone, at 4.1x to 6.1x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Eight large outgoing payments to US recipients were made between 2026-08-06 and 2026-08-13, each exceeding four times the customer’s usual transaction amount, with all transactions rated as statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the nature of the recipient accounts (M944, M876, etc.) and their typical transaction patterns?  
- Are there any known relationships or business activities linking the customer to these recipients?  
- Could the pattern of multiple large payments within a short period reflect a legitimate business transaction or a different type of activity?  

Decision: requires analyst review.

Checks: passed

## C001 (risk score 9)

FLAGGED TRANSACTIONS (system data)
- T04405 | 2026-08-14 18:58 | transfer | $10,583.30 | to X1764 | CY | LARGE_VS_HISTORY; NEW_RECIPIENT_LARGE; FOREIGN_DESTINATION; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 flagged transactions were at least 10x the usual amount of $201.95 (highest: 52.4x).
- 1 of 1 went to a recipient this customer had never paid before.
- 1 of 1 were sent outside the US (CY).
- 1 of 1 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single transaction (T04400) occurred on 2026-08-14 18:58, transferring $10,583.30 to a new recipient in Cyprus, which is 52.4 times the customer’s usual transaction amount and outside the US. The model identified it as statistically unusual, and it was the only flagged transaction with multiple unusual characteristics.

OPEN QUESTIONS FOR THE ANALYST:
- What is the relationship or context behind the transfer to recipient X1764 in Cyprus?
- Why was this transaction initiated at 18:58, a time outside the customer’s usual activity pattern?
- How does the recipient in Cyprus relate to the customer’s known transaction history or network?

Decision: requires analyst review.

Checks: mentions transaction IDs not in the facts: ['T04400']

## C007 (risk score 9)

FLAGGED TRANSACTIONS (system data)
- T04943 | 2026-08-23 13:33 | transfer | $18,229.37 | to X8649 | PA | LARGE_VS_HISTORY; NEW_RECIPIENT_LARGE; FOREIGN_DESTINATION; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 flagged transactions were at least 10x the usual amount of $254.76 (highest: 71.3x).
- 1 of 1 went to a recipient this customer had never paid before.
- 1 of 1 were sent outside the US (PA).
- 1 of 1 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single transaction (T04943) on 2026-08-23 13:33 transferred $18,229.37 to a new recipient in PA, which is 71.3x the customer’s usual transaction amount, sent to an unfamiliar recipient, and outside the US, with the anomaly model identifying it as statistically unusual.

OPEN QUESTIONS FOR THE ANALYST:
- What is the relationship or context behind the recipient X8649 in PA?
- Why was the transaction sent to a foreign destination (PA) when the customer’s usual activity is within the US?
- What is the customer’s typical transaction pattern, and how does this transaction deviate from it?

Decision: requires analyst review.

Checks: passed

## C033 (risk score 9)

FLAGGED TRANSACTIONS (system data)
- T05167 | 2026-08-26 19:30 | transfer | $3,632.05 | to X2846 | KY | LARGE_VS_HISTORY; NEW_RECIPIENT_LARGE; FOREIGN_DESTINATION; ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 flagged transactions were at least 10x the usual amount of $93.85 (highest: 38.8x).
- 1 of 1 went to a recipient this customer had never paid before.
- 1 of 1 were sent outside the US (KY).
- 1 of 1 were rated statistically unusual by the anomaly model.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single transaction (T05167) occurred on 2026-08-26 at 19:30, transferring $3,632.05 to a new recipient in KY, which is 38.8x the customer’s usual transaction amount and outside the US. The transaction was flagged for being unusually large, involving a new recipient, a foreign destination, and a statistically unusual pattern.

OPEN QUESTIONS FOR THE ANALYST:
- What is the nature of the recipient X2846 in KY, and is this a known or previously verified entity?
- Is there any context or background for the customer’s activity in KY or international transfers?
- Why did the anomaly model flag this transaction as statistically unusual, and what specific metric triggered that?

Decision: requires analyst review.

Checks: passed

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

## C023 (risk score 4)

FLAGGED TRANSACTIONS (system data)
- T03538 | 2026-07-31 13:14 | payment | $950.00 | to M771 | US | ML_ANOMALY
- T03643 | 2026-08-02 09:37 | payment | $900.00 | to M856 | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- Up to 6 large outgoing payments (3x usual or more) were made within 7 days.
- 2 of 2 were rated statistically unusual by the anomaly model; 2 for that reason alone, at 6.4x to 7.3x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Two large outgoing payments were made within a 7-day period, each exceeding 6x the customer’s usual transaction amount, with both transactions rated as statistically unusual by the anomaly model.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context or purpose of the customer making large outgoing payments to US entities?  
- Are there any known relationships or accounts associated with the recipients M771 and M856?  
- Could the pattern of large payments within a short timeframe reflect a legitimate business activity or a different transaction pattern?  

Decision: requires analyst review.

Checks: passed

## C003 (risk score 2)

FLAGGED TRANSACTIONS (system data)
- T02469 | 2026-07-12 15:07 | deposit | $796.07 | to SELF | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 were rated statistically unusual by the anomaly model; 1 for that reason alone, at 4.9x to 4.9x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single deposit of $796.07 was made on 2026-07-12 at 15:07, which is 4.9x the customer’s usual transaction amount and was flagged solely due to ML_ANOMALY.  

OPEN QUESTIONS FOR THE ANALYST:  
- Why was the transaction amount 4.9x the customer’s usual amount?  
- What is the context of the deposit to self on 2026-07-12?  
- Is there a pattern of similar transactions in the future or in other accounts?  

Decision: requires analyst review.

Checks: passed

## C011 (risk score 2)

FLAGGED TRANSACTIONS (system data)
- T04738 | 2026-08-20 09:52 | deposit | $2,200.87 | to SELF | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 were rated statistically unusual by the anomaly model; 1 for that reason alone, at 3.3x to 3.3x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single deposit of $2,200.87 was made on 2026-08-20 at 09:52, which is 3.3x the customer’s usual transaction amount and the only flagged transaction. The model identified it as statistically unusual due to its size relative to the median transaction.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context for this deposit? Is it a one-time transaction or part of a pattern?  
- Are there any other transactions or activities from the customer that may explain this deposit?  
- Why was this transaction made at 09:52, a time when no prior transactions occurred and no large outgoing transactions were recorded in the last seven days?  

Decision: requires analyst review.

Checks: passed

## C028 (risk score 2)

FLAGGED TRANSACTIONS (system data)
- T01751 | 2026-07-01 08:44 | payment | $43.53 | to M653 | US | ML_ANOMALY

WHY IT IS UNUSUAL (computed by the system)
- 1 of 1 were rated statistically unusual by the anomaly model; 1 for that reason alone, at 0.3x to 0.3x the usual amount.

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: A single transaction (T01751) occurred at 08:44 on 2026-07-01, amounting to $43.53, which is 0.3x the customer’s usual transaction amount of $139.00. The model identified this as statistically unusual based on its deviation from the median transaction size.

OPEN QUESTIONS FOR THE ANALYST:
- Why was the transaction amount reduced to 0.3x the usual amount, and is this consistent with the customer’s behavior?
- What is the context of the payment to M653, and is there a known relationship or purpose for this recipient?
- Is the timing of the transaction (08:44) consistent with the customer’s typical activity patterns?

Decision: requires analyst review.

Checks: passed
