# FinLLM — Module 1 status (27 Sep 2026)

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
