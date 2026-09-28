## C020 (risk score 4)

SUMMARY: Customer C020 has two deposits to self (T00379 and T00899) that are each 3.6x and 2.2x the customer's usual transaction amount ($437.66), respectively, and were flagged by the model as statistically unusual.

WHAT WAS FLAGGED:
- T00379
- T00899

WHY IT IS UNUSUAL FOR THIS CUSTOMER:
- The model flagged both transactions as statistically unusual due to metrics including: 3.6x and 2.2x the customer's usual transaction amount ($437.66), 1 transaction in the last hour, and 0 large outgoing transactions in the last 7 days.

OPEN QUESTIONS FOR THE ANALYST:
- What is the customer's typical pattern for deposits to self (especially in the US) given the usual median transaction amount of $437.66?
- What specific metrics did the model use to determine these transactions as statistically unusual?
- Are there any other transactions in the last 7 days that might be related to these deposits?

Grounding check: passed
