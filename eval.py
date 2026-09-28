import json
import sys
import time

import chromadb

import config
from llm import ask_llm
from ask import retrieve, build_prompt, SYSTEM_PROMPT, REFUSAL

QUICK = [0, 3, 9, 17, 20]   # Q1, Q4, Q10, Q18, Q21: a fast check for everyday changes


def main():
    quick = "--quick" in sys.argv
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_collection(config.COLLECTION_NAME)
    cases = json.loads((config.BASE_DIR / "eval_questions.json").read_text())
    if quick:
        cases = [cases[i] for i in QUICK]

    retrieval_hits = answer_hits = cited = answerable = 0
    refusal_hits = refusal_cases = 0
    times = []
    start_all = time.time()

    for n, case in enumerate(cases, start=1):
        q = case["question"]
        start = time.time()
        hits = retrieve(collection, q)
        answer = ask_llm(build_prompt(q, hits), system=SYSTEM_PROMPT)
        seconds = time.time() - start
        times.append(seconds)

        pages = [h[2]["page"] for h in hits]
        refused = REFUSAL.lower() in answer.lower()
        wrong_phrase = any(w.lower() in answer.lower() for w in case.get("must_not", []))

        if case["should_refuse"]:
            refusal_cases += 1
            ok = refused
            refusal_hits += ok
            status = "PASS" if ok else "FAIL should have refused"
        else:
            answerable += 1
            got_page = any(p in pages for p in case["expected_pages"])
            got_keywords = (not refused and not wrong_phrase
                            and all(k.lower() in answer.lower() for k in case["keywords"]))
            has_citation = "[" in answer
            retrieval_hits += got_page
            answer_hits += got_keywords
            cited += has_citation
            status = (f"retrieval {'PASS' if got_page else 'FAIL'}  "
                      f"answer {'PASS' if got_keywords else 'FAIL'}  "
                      f"cited {'PASS' if has_citation else 'FAIL'}"
                      + ("  (contains a wrong-answer phrase)" if wrong_phrase else ""))

        print(f"{n:>2}. {q}\n    {status}   [{seconds:.0f}s]\n"
              f"    pages retrieved: {pages}\n    answer: {answer[:150]}\n")

    total = time.time() - start_all
    print("=== EVAL SUMMARY" + (" (quick)" if quick else "") + " ===")
    print(f"Retrieval hit rate:   {retrieval_hits}/{answerable}")
    print(f"Answer correctness:   {answer_hits}/{answerable}")
    print(f"Answers with a cite:  {cited}/{answerable}")
    print(f"Correct refusals:     {refusal_hits}/{refusal_cases}")
    print(f"Time: {total / 60:.1f} min total, {sum(times) / len(times):.0f}s average per question")


if __name__ == "__main__":
    main()
