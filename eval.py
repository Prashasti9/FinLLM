import json
import chromadb

import config
from llm import ask_llm
from ask import retrieve, build_prompt, SYSTEM_PROMPT, REFUSAL


def main():
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_collection(config.COLLECTION_NAME)
    cases = json.loads((config.BASE_DIR / "eval_questions.json").read_text())

    retrieval_hits = answer_hits = cited = answerable = 0
    refusal_hits = refusal_cases = 0

    for n, case in enumerate(cases, start=1):
        q = case["question"]
        hits = retrieve(collection, q)
        pages = [h[2]["page"] for h in hits]
        answer = ask_llm(build_prompt(q, hits), system=SYSTEM_PROMPT)
        refused = REFUSAL.lower() in answer.lower()

        if case["should_refuse"]:
            refusal_cases += 1
            ok = refused
            refusal_hits += ok
            status = "PASS" if ok else "FAIL should have refused"
        else:
            answerable += 1
            got_page = any(p in pages for p in case["expected_pages"])
            got_keywords = (not refused) and all(k.lower() in answer.lower() for k in case["keywords"])
            has_citation = "[" in answer
            retrieval_hits += got_page
            answer_hits += got_keywords
            cited += has_citation
            status = (f"retrieval {'PASS' if got_page else 'FAIL'}  "
                      f"answer {'PASS' if got_keywords else 'FAIL'}  "
                      f"cited {'PASS' if has_citation else 'FAIL'}")

        print(f"{n:>2}. {q}\n    {status}\n    pages retrieved: {pages}\n    answer: {answer[:150]}\n")

    print("=== EVAL SUMMARY ===")
    print(f"Retrieval hit rate:   {retrieval_hits}/{answerable}  (correct page in top {config.TOP_K})")
    print(f"Answer correctness:   {answer_hits}/{answerable}  (contains expected keywords)")
    print(f"Answers with a cite:  {cited}/{answerable}")
    print(f"Correct refusals:     {refusal_hits}/{refusal_cases}")


if __name__ == "__main__":
    main()
