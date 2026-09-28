# FinLLM - Module 1 status (27 Sep 2026)

## How to run
1. python check_setup.py
2. python ingest.py
3. python ask.py            (add --show-context to see retrieved text)
4. python eval.py

## Current eval (24 questions, FFIEC SAR section)
- Retrieval 20/20, answers 19/20, refusals 4/4, confident wrong answers: 0

## Design choices
- Chunks of ~900 characters, 150 overlap; search_document/search_query prefixes for nomic
- Retrieval: top 8 by meaning + up to 4 from a rewritten query + up to 4 from BM25 keywords
  (new methods only ADD chunks, never replace)
- Qwen3 4B, temperature 0, thinking disabled; strict "evidence only, never infer" prompt

## Known issues
- Q4 ("tell the customer a SAR was filed") refuses: page-15 confidentiality chunk not retrieved.
  Safe failure. Candidate fix: reranking.
- Pure prompting does not stop a 4B model inferring; retrieval quality is the real safeguard.
- Latency: 2 Qwen calls per question + up to 16 chunks. Full eval takes ~15-30 min. Not measured per question yet.
- Only one PDF tested so far.

## Model comparison (27 Sep 2026, 24-question eval, read by hand)
- qwen3:4b (thinking): 19/20 correct, 0 confident wrong answers, 4/4 refusals. Very slow; reasoning leaks.
- qwen3:4b-instruct: 17/20 correct, 2 confident wrong answers (Q10, Q20), 4/4 refusals. Faster; clean output.
- Keyword scoring passed both wrong answers; added must_not phrases to the eval.
- Plan: thinking model for regulation Q&A (accuracy-critical), instruct model for explain.py (facts computed in Python).

## Narrative review (27 Sep 2026, qwen3:4b-instruct, read by hand)
- C014, C006, C015, C020: all sections present, first attempt, grounding checks passed.
- Reasoning errors found anyway: C014 claims amounts increase (they do not) and high velocity on all 13 (9 of 13); C015 says all four triggered NEAR_CTR_THRESHOLD (1 did, 3 REPEATED); C020 claims no prior deposits (false) and invents "after 3pm".
- Lesson: code checks catch invented IDs and amounts, not faulty reasoning about real facts.
- Plan: generate WHY IT IS UNUSUAL in Python from reason counts; LLM writes only SUMMARY and OPEN QUESTIONS.

## Detector robustness (27 Sep 2026, 5 unseen datasets, seeds 1-5; tuning used seed 42)
- Precision 92% +/- 5% (85-98%), recall 87% +/- 8% (75-95%), suspicious customers 59/60, innocent flagged 3.4 on average.
- Spending spree (ML only): 53% +/- 25% (15-81%). ML coverage of rule-free patterns is real but unstable.
