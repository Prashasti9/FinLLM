import re
import sys
import json
from datetime import datetime

import ollama
import chromadb
from rank_bm25 import BM25Okapi

import config
from llm import ask_llm

REFUSAL = "I cannot determine this from the supplied documents."

SYSTEM_PROMPT = f"""You are FinLLM, a compliance assistant for bank BSA/AML teams.
Rules:
1. Answer ONLY using the numbered evidence provided. Do not use outside knowledge. Only state what the evidence directly says; never infer or generalize from related examples.
2. Cite evidence after each statement, like [1] or [2][3].
3. Never invent thresholds, deadlines, dollar amounts or rules.
4. If the evidence does not answer the question, reply exactly: {REFUSAL}
5. Be concise: at most 6 sentences or bullet points."""


def rewrite_query(question):
    """Translate a plain-English question into the language regulators write in."""
    prompt = (
        "Rewrite the question below using the formal terminology of a U.S. bank "
        "regulatory (BSA/AML) examination manual. Keep the same meaning. "
        "Return ONLY the rewritten question.\n\n"
        f"Question: {question}"
    )
    return ask_llm(prompt)


def search(collection, text, n):
    """Meaning-based search: text -> numbers -> closest chunks."""
    vector = ollama.embed(
        model=config.EMBED_MODEL,
        input=f"search_query: {text}",
    )["embeddings"][0]
    r = collection.query(query_embeddings=[vector], n_results=n)
    return list(zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0]))


def tokenize(text):
    """Lowercase words and numbers, e.g. 'Initial detection ($5,000)' -> ['initial','detection','$5,000']."""
    return re.findall(r"[a-z0-9$,]+", text.lower())


_bm25 = None
_all_chunks = []


def keyword_search(collection, text, n):
    """Exact-word search (BM25). Built once from all chunks, then reused."""
    global _bm25, _all_chunks
    if _bm25 is None:
        data = collection.get(include=["documents", "metadatas"])
        _all_chunks = list(zip(data["ids"], data["documents"], data["metadatas"]))
        _bm25 = BM25Okapi([tokenize(doc) for _, doc, _ in _all_chunks])
    scores = _bm25.get_scores(tokenize(text))
    ranked = sorted(range(len(_all_chunks)), key=lambda i: scores[i], reverse=True)[:n]
    # BM25 has no 'distance', so mark these with None
    return [(_all_chunks[i][0], _all_chunks[i][1], _all_chunks[i][2], None) for i in ranked]


def retrieve(collection, question, top_k=config.TOP_K, extra=4, show_rewrite=False):
    """Meaning search first; rewrite and keyword search can only ADD new chunks."""
    hits = search(collection, question, top_k)
    seen = {h[0] for h in hits}

    def add_new(candidates):
        added = 0
        for hit in candidates:
            if hit[0] not in seen and added < extra:
                hits.append(hit)
                seen.add(hit[0])
                added += 1

    rewritten = rewrite_query(question)
    if show_rewrite:
        print(f"(also searched as: {rewritten})")
    add_new(search(collection, rewritten, top_k))      # extra chunks from the rewrite
    add_new(keyword_search(collection, question, top_k))  # extra chunks from exact words
    return hits


def build_prompt(question, hits):
    """Number each chunk so the model can cite it as [1], [2], ..."""
    evidence = ""
    for n, (_, text, meta, _) in enumerate(hits, start=1):
        evidence += f"\n[{n}] ({meta['source']}, page {meta['page']})\n{text}\n"
    return f"EVIDENCE:\n{evidence}\nQUESTION: {question}"


def log(question, hits, answer):
    """Append one line per question to logs/qa_log.jsonl — the audit trail."""
    config.LOG_DIR.mkdir(exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "retrieved_ids": [h[0] for h in hits],
        "answer": answer,
    }
    with open(config.LOG_DIR / "qa_log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


def main():
    show_context = "--show-context" in sys.argv
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_collection(config.COLLECTION_NAME)
    print(f"FinLLM ready — {collection.count()} chunks loaded. Type 'exit' to quit.\n")

    while True:
        question = input("Ask FinLLM > ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        hits = retrieve(collection, question, show_rewrite=True)
        answer = ask_llm(build_prompt(question, hits), system=SYSTEM_PROMPT)

        print("\n--- ANSWER ---")
        print(answer)
        print("\n--- SOURCES ---")
        for n, (_, text, meta, dist) in enumerate(hits, start=1):
            how = f"distance {dist:.3f}" if dist is not None else "keyword match"
            print(f"[{n}] {meta['source']}, page {meta['page']}  ({how})")
            if show_context:
                print(f"    {text[:400]}...\n")
        print()

        log(question, hits, answer)


if __name__ == "__main__":
    main()
