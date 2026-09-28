## C020 (risk score 4)

FLAGGED TRANSACTIONS (system data)
- T00379 | 2026-06-07 15:11 | deposit | $1,399.54 | to SELF | US | ML_ANOMALY
- T00899 | 2026-06-16 12:37 | deposit | $1,111.63 | to SELF | US | ML_ANOMALY

ANALYST NARRATIVE (AI-drafted, verify before use)
SUMMARY: Two deposits to self were flagged between 2026-06-07 and 2026-06-16, each exceeding the customer’s usual transaction amount by a statistically notable margin.  

WHY IT IS UNUSUAL FOR THIS CUSTOMER:  
- Both flagged transactions were deposits to self, which is uncommon for a customer with no prior history of such activity.  
- Each transaction is significantly above the median usual amount ($437.66), with one being 3.6x and the other 2.2x that amount.  
- The transactions occurred during non-peak hours (after 3pm), and there were no large outgoing transactions in the 7 days prior to either.  
- Both transactions were flagged solely by the ML_ANOMALY model, indicating statistical deviation without other behavioral indicators.  

OPEN QUESTIONS FOR THE ANALYST:  
- What is the customer’s typical behavior around deposits to self, and is this pattern consistent with known activity?  
- Are there any known account changes, such as a new account or product setup, that could explain the deposit activity?  
- Could the flagged transactions be part of a larger pattern of activity that has not yet been detected?  

Decision: requires analyst review.

Checks: passed
