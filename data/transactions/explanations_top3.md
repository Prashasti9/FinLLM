## C014 (risk score 75)

SUMMARY:  
A sequence of 13 transfers occurred between 2026-08-17 02:02 and 02:47, all to new recipients, with activity concentrated in the early hours of the morning and increasing in volume and amount over time.  

WHAT WAS FLAGGED:  
- T04531 | $251.71 | to N4146 | US | 2.4x usual | 1 txns in last hour  
- T04532 | $269.58 | to N1172 | US | 2.6x usual | 2 txns in last hour  
- T04533 | $211.13 | to N7811 | US | 2.0x usual | 3 txns in last hour  
- T04534 | $332.93 | to N7301 | US | 3.2x usual | 4 txns in last hour  
- T04535 | $239.69 | to N1534 | US | 2.3x usual | 5 txns in last hour  
- T04536 | $185.23 | to N4565 | US | 1.8x usual | 6 txns in last hour  
- T04537 | $332.24 | to N7696 | US | 3.1x usual | 7 txns in last hour  
- T04538 | $233.77 | to N5370 | US | 2.2x usual | 8 txns in last hour  
- T04539 | $324.60 | to N5362 | US | 3.0x usual | 9 txns in last hour  
- T04540 | $344.13 | to N3057 | US | 3.2x usual | 10 txns in last hour  
- T04541 | $228.27 | to N7738 | US | 2.1x usual | 11 txns in last hour  
- T04542 | $208.68 | to N9501 | US | 1.9x usual | 12 txns in last hour  
- T04543 | $291.99 | to N1769 | US | 2.7x usual | 13 txns in last hour  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- All 13 transactions occurred between midnight and 6am, which is outside the customer’s usual activity period.  
- Every transaction was to a new recipient, with no prior transfers to any of these accounts.  
- The number of transactions per hour increased from 1 to 13 over the 45-minute period, indicating a rapid escalation in transaction volume.  
- The model flagged 11 transactions as ML_ANOMALY, citing statistical

Checks: missing sections after 2 attempts: ['OPEN QUESTIONS', 'Decision:']

## C006 (risk score 61)

SUMMARY:  
A sequence of 11 transfers occurred between 2026-08-19 02:04 and 02:45, all to new recipients, with transaction amounts 2.0x to 3.2x the customer’s usual amount of $101.62.  

WHAT WAS FLAGGED:  
- T04668 | $269.09 | to N5723 | 2.6x usual | 1 txns in last hour | 2 days since previous txn | 0 large outgoing in last 7 days  
- T04669 | $276.05 | to N4617 | 2.7x usual | 2 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04670 | $333.63 | to N6151 | 3.2x usual | 3 txns in last hour | 0 days since previous txn | 1 large outgoing in last 7 days  
- T04671 | $276.19 | to N6146 | 2.7x usual | 4 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04672 | $239.09 | to N4233 | 2.3x usual | 5 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04673 | $211.92 | to N5501 | 2.0x usual | 6 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04674 | $295.23 | to N8347 | 2.8x usual | 7 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04675 | $233.51 | to N1907 | 2.2x usual | 8 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04676 | $240.57 | to N8667 | 2.2x usual | 9 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T04677 | $347.53 | to N7910 | 3.2x usual | 10 txns in last hour | 0 days since previous txn | 2 large outgoing in last 7 days  
- T04678 | $342.71 | to N4831 | 3.1x usual | 11 txns in last hour | 0 days since previous txn | 3 large outgoing in last 7 days  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- The

Checks: missing sections after 2 attempts: ['OPEN QUESTIONS', 'Decision:']

## C015 (risk score 30)

SUMMARY: Four deposits to self were flagged between 2026-08-01 and 2026-08-04, each exceeding 45x the customer’s usual transaction amount of $205.24.  

WHAT WAS FLAGGED:  
- T03612 | 2026-08-01 15:47 | deposit | $9,528.43 | to SELF | US | 47.1x usual | 1 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T03671 | 2026-08-02 15:17 | deposit | $9,282.83 | to SELF | US | 45.6x usual | 1 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  
- T03699 | 2026-08-03 09:22 | deposit | $9,531.97 | to SELF | US | 46.8x usual | 1 txns in last hour | 1 days since previous txn | 0 large outgoing in last 7 days  
- T03812 | 2026-08-04 17:58 | deposit | $9,286.45 | to SELF | US | 45.6x usual | 2 txns in last hour | 0 days since previous txn | 0 large outgoing in last 7 days  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- All four transactions are deposits to self, with amounts between $9,282 and $9,532, which are 45.6x to 47.1x the customer’s usual transaction amount of $205.24.  
- The customer has made four cash deposits between $9,000 and $9,999 in a span of three days, with at least two such deposits within 7 days (REPEATED_NEAR_CTR_THRESHOLD).  
- Each transaction is flagged by ML_ANOMALY, indicating the model identified it as statistically unusual based on deviation from historical patterns.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer’s typical purpose for deposits to self, and is there a known pattern of such activity?  
- Are there any other transactions (e.g., outgoing, transfers) that occurred during this period that might explain the deposits?  
- Could the deposits be part of a legitimate activity, such as a one-time cash infusion or a personal financial event, that is not reflected in the customer history?  

Decision: requires analyst review.

Checks: amount $9,282 not found in the facts (invented or rounded); amount $9,532, not found in the facts (invented or rounded)
