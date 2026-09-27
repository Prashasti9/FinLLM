# FinLLM — Project Brief for Claude Code

> Save this file as `CLAUDE.md` in the repo root so Claude Code reads it automatically at the start of every session.

---

## 1. What we are building

**FinLLM** is a private, locally hosted AI financial analyst focused on **fraud investigation and compliance (AML/KYC)**.

It reads financial policy documents and transaction data and produces **evidence-backed answers and investigation reports**. No sensitive data is sent to external AI APIs.

**Why local:** fintechs and compliance teams are reluctant to send customer or transaction data to third-party LLM APIs. Running local open-source models is part of the pitch, not just a cost choice.

**Longer-term vision (context only, do not build yet):** FinLLM is the proof of concept for **FinSight AI**. That is a real-time "should this financial action be allowed?" risk API, sold to smaller fintechs, lenders, payment startups and marketplaces. It would combine rules, ML scoring, graph-based fraud-ring detection and an LLM investigator.

**Team:** Udit and Kartik (co-founders).

---

## 2. Decisions already made

| Decision | Choice | Reason |
|---|---|---|
| Budget for POC | **$0**: all open-source, runs on a laptop | Prove value before spending |
| First use case | **Fraud investigation + compliance** | Strongest pain point; links to the FinSight vision |
| LLM | **Qwen3 4B via Ollama** (`qwen3:4b`) | Runs locally on modest hardware |
| Embeddings | **`nomic-embed-text` via Ollama** | Local and small (~274 MB) |
| Vector DB | **ChromaDB** (persistent, local), v1.5.x | Open source, zero setup |
| PDF parsing | **pypdf** | Simple; text-based PDFs only for now |
| Fine-tuning | **No.** Base model + RAG + prompts first | Fine-tune only if evaluation shows a gap |
| Core principle | **ML/rules detect → LLM explains** | The LLM never makes the final fraud or compliance decision |

### Explicitly out of scope for now
- **Tools to leave out for now:** LangChain, Neo4j, Kafka, Redis, cloud deployment, paid APIs.
- **No lending/credit, payments or money movement.**
- **No model training from scratch** and no fine-tuning.
- **Dashboard only later:** don't build a UI until the Module 1 CLI works end-to-end (Streamlit comes later).

---

## 3. Current state (as of 27 Sep 2026)

Working on Kartik's Windows laptop (Python 3.12):

- ✅ Python venv, Ollama, `qwen3:4b`, `nomic-embed-text` pulled
- ✅ `pip install ollama chromadb pypdf`
- ✅ `test_ollama.py`: Python → Ollama → Qwen3 chat works
- ✅ `rag_test.py`: 3 hard-coded fintech paragraphs → embeddings → ChromaDB → retrieval → Qwen answer works
- ✅ Folders `data/policies/` and `chroma_db/` created
- ⏳ **Next step:** ingest a real AML/compliance PDF (`data/policies/aml_policy.pdf`) and answer questions with **filename + page citations**

The existing scripts are throwaway prototypes. Replace them with the structured project below.

---

## 4. Target repo structure

```
FinLLM/
├── CLAUDE.md                 # this file
├── README.md                 # setup + usage for humans
├── requirements.txt          # pinned versions
├── .gitignore                # .venv/, chroma_db/, data/raw large files, __pycache__/
├── config.py                 # model names, paths, chunk size, top_k: one place
├── finllm/
│   ├── __init__.py
│   ├── llm.py                # thin wrapper around ollama.chat (think=False by default)
│   ├── embeddings.py         # wrapper around ollama.embed (batching)
│   ├── ingest.py             # PDF → pages → chunks → embeddings → Chroma
│   ├── retrieve.py           # query → top-k chunks with metadata
│   ├── answer.py             # builds grounded prompt, returns answer + citations
│   └── prompts.py            # all system prompts in one file
├── scripts/
│   ├── ingest_docs.py        # CLI: ingest everything in data/policies/
│   └── ask.py                # CLI: interactive Q&A loop
├── data/
│   ├── policies/             # AML/KYC/fraud policy PDFs
│   └── transactions/         # (Module 2) CSVs
├── eval/
│   ├── questions.jsonl       # test questions + expected page(s)
│   └── run_eval.py           # retrieval hit-rate + citation check
└── tests/
```

The code must work on **both Windows and macOS** (use `pathlib`, no hard-coded backslashes).

---

## 5. Build plan

Work **one module at a time**. Each module ends with a runnable command and a check of its acceptance criteria before moving on.

### Module 0: Project skeleton (do first)
- Create the structure above, `requirements.txt` with pinned versions, `.gitignore` and `config.py`.
- `README.md` should contain setup steps for Windows and Mac:
  - Install Python 3.11+ and Ollama.
  - Run `ollama pull qwen3:4b` and `ollama pull nomic-embed-text`.
  - Create and activate a venv.
  - Run `pip install -r requirements.txt`.
- Add a `scripts/check_setup.py` that verifies all of the following, with clear pass/fail messages:
  - Ollama is running.
  - Both models are present.
  - ChromaDB imports.
  - A 1-sentence chat round-trip works.

**Done when:** `python scripts/check_setup.py` prints all green on a fresh machine.

### Module 1: Financial Document RAG (current focus)

**Ingestion (`scripts/ingest_docs.py`):**
- Read every PDF in `data/policies/`, page by page, with pypdf.
- **Chunking:**
  - Split each page into chunks of ~800–1,000 characters with ~150 character overlap.
  - Never embed whole pages. Long inputs get silently truncated by the embedding model.
- **Metadata** on each chunk: `source` (filename), `page`, `chunk_index`.
- Chunk IDs must be deterministic (e.g. `{filename}_p{page}_c{i}`), so re-running ingestion upserts instead of duplicating.
- **Warnings:**
  - Warn and skip pages with no extractable text; these are likely scanned images.
  - Print a summary: files, pages, chunks and pages skipped.
- Embed in batches and use one Chroma collection: `fintech_policies`.

**Question answering (`scripts/ask.py`):**
- Interactive loop: user asks a question and gets an answer.
- Retrieve the top-k chunks (default 5, configurable).
- The prompt tells the model to:
  - Answer ONLY from the supplied evidence.
  - Cite `filename, page` for every claim.
  - Reply exactly `I cannot determine this from the supplied documents.` when the evidence is insufficient.
- Call Qwen with `think=False` (Qwen3's thinking mode makes responses very slow on a laptop).
- Print, in order:
  - The answer.
  - A "Retrieved sources" list (file, page, similarity score).
  - A `--show-context` flag that prints the retrieved chunks, for debugging.
- Log each Q&A (timestamp, question, retrieved chunk IDs, answer) to `logs/qa_log.jsonl`. This is the start of the audit trail.

**Evaluation (`eval/`):**
- Create 10–15 questions about the ingested PDF, with the page(s) where each answer lives.
- Include 2–3 questions the PDF does NOT answer, to check that the refusal sentence works.
- `run_eval.py` reports:
  - Retrieval hit rate (was the correct page in the top-k?).
  - Whether each answer cites a page.
  - Refusal correctness.

**Done when:** you can ask a real question about an AML PDF and get a correct answer with the right page cited. The eval also runs and prints its metrics.

**Test data:** use a public, text-based AML document. Suggested: one chapter of the **FFIEC BSA/AML Examination Manual** (bsaaml.ffiec.gov) or a **FinCEN** guidance PDF. Save it as `data/policies/aml_policy.pdf`, or any name; ingestion handles all PDFs in the folder.

### Module 2: Transaction Analyst
- **Data:** load a transactions CSV into pandas/SQLite. Use a public synthetic fraud dataset, e.g. PaySim or IBM AML synthetic data, subsampled.
- **Detection (no LLM here):**
  - Simple rules, e.g. amount > X, new beneficiary, velocity.
  - Isolation Forest from scikit-learn.
- **Output:** a flagged list with reason codes (e.g. `new_beneficiary`, `amount_8x_customer_avg`).
- **LLM step:** the LLM receives the flags and reason codes and writes a plain-English explanation. It does not decide what is suspicious.

### Module 3: Compliance Assistant
- Input: a transaction ID.
- The system:
  1. Pulls the transaction and its flags (Module 2).
  2. Retrieves the relevant policy clauses (Module 1).
  3. Asks the LLM whether policy says to escalate, citing both the transaction evidence and the policy page.
- Output: a recommendation + evidence + "requires human decision" label.

### Module 4: Investigation Agent (demo "wow" moment)
- Input: `Investigate customer C192`.
- The agent gathers:
  - The customer's transaction history.
  - Flags and anomaly scores.
  - The relevant policy clauses.
  - Prior alerts.
- It outputs a structured **case report**:
  - Summary.
  - Risk factors with evidence.
  - Relevant policy citations.
  - Recommended next action.
  - Open questions.
- Plain Python tool-calling loop. No agent frameworks.

### Later (only after Modules 1–4 work)
- Streamlit UI for demos
- FastAPI endpoints (e.g. `POST /investigate`)
- Larger model (e.g. Qwen3 8B) if 4B quality is insufficient
- Case-review screen where human decisions become labeled training data

---

## 6. Engineering rules

1. **Grounding over fluency.** Every answer must be traceable to a document page or data row. If it isn't, the system says so.
2. **Deterministic logic for decisions.** Thresholds, rules and scores live in Python, not in prompts.
3. **Keep it small.** Before adding a dependency, check whether ~30 lines of plain Python would do. Justify any new package in the commit message.
4. **Config in one place** (`config.py`): model names, paths, chunk size, top_k.
5. **Everything runnable from the CLI** with a single command, and documented in the README.
6. **Log everything** (JSONL), because compliance buyers will ask for an audit trail.
7. **Test on both Windows and Mac** paths; both co-founders run it locally.
8. Use git from day one; commit after each module passes its acceptance criteria.

---

## 7. First instruction to Claude Code

> Read CLAUDE.md. Build **Module 0**, then **Module 1**, exactly as specified. Stop after Module 1 and show me:
> - how to run ingestion, Q&A and the eval;
> - the eval results on the PDF in `data/policies/`.
>
> Don't start Module 2.

---

## 8. Business validation (parallel track, non-code)

The tech stack is not the moat. By the end of Module 3–4, demo to **3–5 compliance, fraud or fintech-risk practitioners** and learn:
- Which investigation step eats the most analyst time today?
- Would they trust a local model's case summary? What evidence would they need to see?
- What would they pay to automate, and who signs off on buying it?

Use their answers to decide whether FinLLM stays a compliance/investigation tool or narrows toward the FinSight fraud-risk API.

## 9. Virtual environment (mandatory)
- Always use the project venv at `.venv`.
- Install packages with `.venv/bin/pip`; run scripts with `.venv/bin/python`.
- Never install packages globally. Record every package in requirements.txt.
