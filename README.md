# FinLLM

A local AI assistant for anti-money-laundering (AML) compliance work. It answers questions from regulatory guidance with page citations, flags unusual transactions using rules and anomaly detection, and writes alert summaries for a human analyst to review.

Everything runs on a laptop. No data is sent to an external AI API.

## Why

Bank compliance analysts spend much of their time on alert review: working out what a customer did, looking up what the regulations require, and writing up the case. This project explores how much of that evidence gathering can be automated while keeping every statement traceable to a transaction or a regulation page, and keeping the final decision with a person.

Design principle: rules and ML detect, the LLM explains, a human decides.

## What it does

**Module 1: Regulation Q&A**
- Ingests a regulatory PDF (FFIEC BSA/AML Examination Manual, Suspicious Activity Reporting section) into a local vector database.
- Answers questions using only retrieved evidence, cites page numbers, and refuses when the document does not cover the question.
- Logs every question and answer for an audit trail.

**Module 2: Transaction analysis**
- Generates synthetic bank transactions with planted suspicious patterns (structuring, large foreign transfers, velocity bursts, dormant account reactivation, spending sprees).
- Flags transactions using rule-based checks with reason codes plus an Isolation Forest anomaly model.
- Writes a per-customer alert narrative with an LLM. The transaction list and all numbers come from Python; the LLM writes only the narrative, which is checked by code for invented transaction IDs, invented amounts, missing sections and accusatory language.

## Architecture

    Module 1
    PDF -> chunks (900 chars, 150 overlap) -> nomic-embed-text -> ChromaDB
    question -> dense search + query rewrite + BM25 keyword search -> evidence
             -> Qwen3 4B -> cited answer or refusal -> audit log

    Module 2
    transactions -> features (per-customer history) -> rules + Isolation Forest
                 -> flags with reason codes -> fact sheet (Python)
                 -> Qwen3 4B narrative -> grounding and format checks

## Results

All results are on a single 17-page document and on synthetic transaction data I generated. They show that the approach works on this setup, not how it would perform on real bank data.

**Module 1** (24-question eval: 20 answerable, 4 out of scope; answers read by hand)

| Model | Correct answers | Confident wrong answers | Correct refusals |
|---|---|---|---|
| qwen3:4b (thinking) | 19/20 | 0 | 4/4 |
| qwen3:4b-instruct | 17/20 | 2 | 4/4 |

The correct page was retrieved for 20/20 answerable questions with both models. The instruct model is faster but gave two confidently wrong answers that the thinking model got right, so model choice here is a latency versus accuracy trade-off.

**Module 2** (5,343 transactions, 12 customers with planted patterns)

| Metric | Result |
|---|---|
| Precision | 91% |
| Recall | 88% |
| Suspicious customers caught (via an actual suspicious transaction) | 12/12 |
| Innocent customers flagged | 4 |
| Spending-spree pattern (no rule covers it), caught by ML only | 10/17 |

## What I learned

- **Evals catch what spot checks miss.** Adding query rewriting looked like an improvement but dropped the score from 7/8 to 6/8, because results from two different searches were ranked by distance scores that are not comparable. Changing new retrieval methods so they only add evidence, never replace it, fixed this.
- **Hybrid search was needed for precise regulatory wording.** Dense search missed the page defining "initial detection" and the model answered confidently and wrongly. BM25 keyword search retrieved the right page.
- **Prompting alone did not stop a small model from inferring.** A stricter "never infer" rule had no effect on the wrong answer. Better retrieval did.
- **Keyword-based scoring can pass wrong answers.** Two confidently wrong answers passed because they contained the expected word. The eval now also checks for wrong-answer phrases, and key answers are read by hand.
- **The ML only helped once it had the right features.** On a pattern no rule covers, Isolation Forest caught 0/17 transactions. A 7-day behavioral feature raised this to 5/17, and removing rare yes/no features, which the model was over-isolating, raised it to 10/17 and precision from 72% to 91%.
- **Unsupervised ML detects unusual, not criminal.** Its remaining false alarms have no rule reason, so the narratives must describe the numbers without implying wrongdoing.
- **Check exactly which model you are running.** The default qwen3:4b tag was the thinking-only variant. That caused leaked reasoning, slow responses and format failures that looked like prompt problems.
- **Check the context window.** Ollama defaulted to 4,096 tokens, smaller than some prompts, which silently truncates the system prompt. It is now set to 8,192.
- **Let code do what code is good at.** The LLM copied transaction details and ran out of output tokens. Python now prints the transaction table and the LLM writes only the narrative.

## Project structure

    config.py                  settings: models, paths, chunk size, top-k
    check_setup.py             verifies Ollama, models, libraries and data
    llm.py                     wrapper for the local LLM
    ingest.py                  PDF -> chunks -> embeddings -> ChromaDB
    ask.py                     interactive cited Q&A with hybrid retrieval
    eval.py                    Module 1 evaluation (--quick for 5 key questions)
    eval_questions.json        24 test questions with expected pages
    find_page.py               finds which page a phrase appears on
    generate_transactions.py   synthetic transactions with planted patterns
    detect.py                  rules + Isolation Forest -> flags.csv
    eval_detect.py             Module 2 evaluation against the answer key
    explain.py                 per-customer alert narratives with checks
    data/policies/             regulatory PDF
    data/transactions/         generated data, flags and narratives

## Setup

Requirements: Python 3.11+, Ollama, about 6 GB of free disk space, 8 GB+ RAM.

    ollama pull qwen3:4b-instruct
    ollama pull nomic-embed-text

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python check_setup.py

## Usage

    # Module 1
    python ingest.py
    python ask.py --show-context
    python eval.py --quick
    python eval.py

    # Module 2
    python generate_transactions.py
    python detect.py
    python eval_detect.py
    python explain.py            # top 3 customers by risk
    python explain.py C020       # one customer

## Limitations

- Tested on one regulatory document and synthetic transactions only.
- The anomaly model is unsupervised. With labeled data, a supervised model would likely perform better.
- Code checks catch invented facts but not faulty reasoning about real facts. Narratives still need human review.
- Local inference on a laptop is slow: roughly a minute per question in the full evaluation.

## Next steps

- Use the thinking model for regulation Q&A and the instruct model for narratives.
- Reduce latency: rewrite queries only when needed, and send fewer chunks.
- Link each flag to the relevant regulation (Module 3).
- Train and compare a supervised model on a public labeled dataset (PaySim or IBM AML).
- Build a batch pipeline that stores runs and results in SQLite, and a simple review interface.

## Authors

Prashasti Srivastava and Kartik. Add who built which parts.
