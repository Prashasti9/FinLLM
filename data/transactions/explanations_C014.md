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
