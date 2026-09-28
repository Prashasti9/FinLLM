## C020 (risk score 4)

SUMMARY: Two deposits to self were flagged as statistically unusual, each significantly exceeding the customer’s usual transaction amount.  

WHAT WAS FLAGGED:  
- T00379 | 2026-06-07 15:11 | deposit | $1,399.54 | to SELF | US | 3.6x usual | 1 txns in last hour | 6 days since previous txn | 0 large outgoing in last 7 days  
- T00899 | 2026-06-16 12:37 | deposit | $1,111.63 | to SELF | US | 2.2x usual | 1 txns in last hour | 5 days since previous txn | 0 large outgoing in last 7 days  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- The customer typically deposits amounts around $437.66, but both transactions are significantly larger—T00379 is 3.6x usual, T00899 is 2.2x usual.  
- Both transactions are deposits to self, which is not typical for a customer with a history of 116 transactions all in the US.  
- Each transaction occurs with only one transaction in the last hour, and there are no large outgoing transactions in the 7 days prior.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the context of the large deposits—were they part of a known recurring pattern or a one-time event?  
- Is there a reason the customer might be making deposits to self at this scale, such as a personal financial event or a change in behavior?  
- Could the model’s ML_ANOMALY flag be due to a statistical outlier rather than a behavioral shift?  

Decision: requires analyst review.

Checks: passed
