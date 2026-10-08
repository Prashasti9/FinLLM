
import chromadb
import ollama

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="finllm_policy_chunks_v1"
)

print(f"Connected: {collection.count()} chunks", flush=True)

question = input("\nAsk FinLLM: ").strip()

if not question:
    raise SystemExit("Please enter a question.")

searches = {
    "kyc_policy.pdf": (
        "Suspicious transaction indicators, large and complex "
        "transactions, unusual patterns, inconsistent customer "
        "activity, unexplained transactions and no economic rationale"
    ),
    "msb_prevention_guide.pdf": (
        "Suspicious activity indicators, transaction structuring, "
        "unusual money transfer patterns, suspicious customer "
        "behavior and money laundering red flags"
    )
}

# Prefer excerpts containing concrete indicators
keywords = {
    "unusual": 3,
    "inconsistent": 3,
    "structur": 3,
    "economic rationale": 3,
    "suspicious activity": 3,
    "unexplained": 3,
    "complex": 2,
    "pattern": 2,
    "evad": 2,
    "conceal": 2,
    "kiting": 2,
    "legitimate purpose": 2,
    "large transaction": 1
}

evidence = []
evidence_text = ""

for filename, search_text in searches.items():

    print(f"\nSearching: {filename}", flush=True)

    embedding = ollama.embed(
        model="nomic-embed-text",
        input=search_text
    )["embeddings"][0]

    results = collection.query(
        query_embeddings=[embedding],
        n_results=10,
        where={"source": filename}
    )

    candidates = []

    for rank, (document, metadata) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        lower_text = document.lower()

        score = sum(
            weight
            for keyword, weight in keywords.items()
            if keyword in lower_text
        )

        # Small preference for semantic search ranking
        score += (10 - rank) * 0.1

        candidates.append((score, document, metadata))

    candidates.sort(key=lambda item: item[0], reverse=True)

   # Select two different pages for EACH document
    selected = []
    used_pages = set()

    for candidate in candidates:
        page = candidate[2]["page"]

        if page in used_pages:
            continue

        selected.append(candidate)
        used_pages.add(page)

        if len(selected) == 2:
            break

    for score, document, metadata in selected:
        label = f"E{len(evidence) + 1}"
        source = metadata["source"]
        page = metadata["page"]
        jurisdiction = metadata["jurisdiction"]

        evidence.append(
            f"[{label}] {source}, PDF page {page}"
        )

        evidence_text += (
            f"\n[{label}]\n"
            f"DOCUMENT: {source}\n"
            f"JURISDICTION: {jurisdiction}\n"
            f"PDF PAGE: {page}\n"
            f"CONTENT:\n{document}\n"
        )

        print(
            f"Selected [{label}]: {source}, PDF page {page}",
            flush=True
        )

# This section is OUTSIDE the document loop
if len(evidence) < 4:
    raise SystemExit(
        "Insufficient evidence. Expected two pages "
        "from each document."
    )
print("\nGenerating answer...", flush=True)

stream = ollama.chat(
    model="qwen3:4b",
    think=False,
    stream=True,
    messages=[
        {
            "role": "system",
            "content": (
                "You are FinLLM, a financial compliance assistant. "
                "Answer in no more than 150 words. "
                "Start with the suspicious transaction indicators "
                "that are supported by BOTH documents. "
                "For each common indicator, cite at least one "
                "Indian KYC evidence label and one US FinCEN "
                "evidence label, such as [E1] and [E3]. "
                "Then briefly identify indicators mentioned "
                "in only one document. "
                "Use only the supplied evidence. "
                "Do not invent information or assume historical "
                "guidance represents current law. "
                "If no common indicators are supported, say so."
            )
        },
        {
            "role": "user",
            "content": (
                f"QUESTION:\n{question}\n\n"
                f"EVIDENCE:\n{evidence_text}"
            )
        }
    ],
    options={
        "num_ctx": 4096,
        "num_predict": 450,
        "temperature": 0
    }
)

print("\n========== FINLLM ANSWER ==========\n")

for chunk in stream:
    print(
        chunk["message"]["content"],
        end="",
        flush=True
    )

print("\n\n========== EVIDENCE SOURCES ==========")

for reference in evidence:
    print(reference)

print("\nTest finished.")