# FinLLM: One-Page Brief

**What it is:** a local AI assistant for anti-money-laundering (AML) compliance. It answers regulation questions with page citations, flags unusual bank transactions, and drafts alert narratives for a human analyst. Everything runs on a laptop; no data goes to an external AI API.

**Principle:** rules and ML detect, the LLM explains, a human decides.

**Stack:** Ollama (Qwen3 4B, nomic-embed-text), ChromaDB, BM25, pypdf, pandas, scikit-learn. Code: github.com/Prashasti9/FinLLM.

## Built so far

**Module 1: Regulation Q&A**
- FFIEC Suspicious Activity Reporting guidance (17 pages) chunked and indexed.
- Hybrid retrieval: meaning-based search, an LLM query rewrite and keyword search (BM25).
- Answers only from evidence, cites pages, refuses when the document does not cover the question, logs every answer.
- 24-question evaluation: correct page found 20/20. Thinking model 19/20 correct with 0 confident wrong answers; faster instruct model 17/20 with 2 confident wrong answers.

**Module 2: Transaction analysis**
- Synthetic bank data (50 customers, 90 days) with 5 planted suspicious patterns.
- Detector: rule-based reason codes plus an Isolation Forest anomaly model.
- On 5 unseen datasets: precision 92% +/- 5%, recall 87% +/- 8%, 59 of 60 suspicious customers caught.
- Alert narratives: Python computes every fact and the "why unusual" section; the LLM writes only the summary and open questions; code checks for invented IDs, invented amounts and accusatory language. 16/16 complete, 15/16 passed checks, about 6 seconds each.

## Main lessons
- Evaluations caught regressions that spot checks missed.
- Keyword search was needed for precise regulatory wording.
- Prompting could not stop a small model from inferring; better retrieval and giving the LLM less freedom did.
- Features mattered more than the algorithm for the ML.
- Model variant and context window settings caused problems that looked like prompt issues.
- Speed and accuracy trade off: the faster model made confident errors.

## Next
Split models by task (accurate model for regulation Q&A, fast model for narratives), reduce latency, link flags to regulations (Module 3), train a supervised model on public labeled data, build a small pipeline and review UI, and show the demo to AML practitioners.

**Caveat:** results are on one document and synthetic data; they show the approach works, not real-world performance.
