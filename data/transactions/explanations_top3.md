## C014 (risk score 75)

SUMMARY: Customer C014 has 13 transactions within a 45-minute window on 2026-08-17, each to a new US recipient, with amounts 2.4x to 3.2x the customer's usual transaction amount ($103.60), and all occurring between midnight and 6am.

WHAT WAS FLAGGED:  
- T04531, T04532, T04533, T04534, T04535, T04536, T04537, T04538, T04539, T04540, T04541, T04542, T04543

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- The customer has 13 new US recipients in a short period (45 minutes), which deviates significantly from their historical transaction pattern (128 transactions over 2026-06-03 to 2026-08-28).  
- All transactions occurred between midnight and 6am, a time window not aligned with the customer's typical activity hours (based on historical data).  
- The model flagged 11 transactions as statistically unusual, indicating a high deviation from the customer's baseline behavior (e.g., transaction volume, recipient patterns, and timing).

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer's typical activity pattern during nighttime hours?  
- Why does the customer have 13 new US recipients in such a short timeframe?  
- Which specific transactions were flagged as statistically unusual by the model, and what metrics caused the flag?  

DECISION: Requires analyst review to investigate the context, validate unusual patterns, and determine next steps.

Checks: passed

## C006 (risk score 61)

SUMMARY: Customer C006 has 11 flagged transactions (totaling $3,065.52) occurring during the night (2026-08-19 02:04 to 02:45), with each transaction exceeding the customer's typical transaction amount (median of $101.62) by 2.0x to 3.2x, and all transfers directed to new recipients in the US.

WHAT WAS FLAGGED:
- T04668
- T04669
- T04670
- T04671
- T04672
- T04673
- T04674
- T04675
- T04676
- T04677
- T04678

WHY IT IS UNUSUAL FOR THIS CUSTOMER:
- The customer executed 11 transfers to new US recipients within a 41-minute window during the night (2026-08-19 02:04 to 02:45), significantly exceeding their typical transaction amount (2.0x to 3.2x).
- Transactions demonstrated increasing velocity (from 1 to 11 transactions within the last hour), indicating rapid escalation.
- The model flagged 9 of the 11 transactions as statistically unusual based on behavioral patterns.

OPEN QUESTIONS FOR THE ANALYST:
- What is the customer's historical transaction pattern during nighttime hours to contextualize the observed activity?
- Are there legitimate explanations (e.g., recurring business needs, system errors) for the rapid sequence of transfers to new US recipients?

Decision: requires analyst review.

Checks: passed

## C015 (risk score 30)

### Summary  
Customer C015 has 4 deposits to self (T03612, T03671, T03699, T03812) in the US between 2026-08-01 and 2026-08-04 with amounts of $9,528.43, $9,282.83, $9,531.97, and $9,286.45, each being 45.6x to 47.1x the customer's usual transaction amount of $205.24.  

### Why This Is Unusual  
- The deposits (T03612, T03671, T03699, T03812) are in the US and each has an amount of $9,528.43, $9,282.83, $9,531.97, and $9,286.45 respectively, and each is 45.6x to 47.1x the customer's usual transaction amount of $205.24.  
- The model identified all 4 deposits as statistically unusual.  

### Open Questions for Analysis  
1. What is the customer's historical pattern of deposits to self (US) in the past 30 days?  
2. What specific anomaly metrics (e.g., threshold, standard deviation) were used to flag these transactions?  
3. Are there any other transactions (outside the flagged period) that might be related to these deposits?  

### Decision  
Requires analyst review to investigate the context, validate the statistical model, and determine potential risks or legitimate activity.

Checks: missing sections after 2 attempts: ['SUMMARY:', 'WHAT WAS FLAGGED:', 'WHY IT IS UNUSUAL', 'Decision:']
