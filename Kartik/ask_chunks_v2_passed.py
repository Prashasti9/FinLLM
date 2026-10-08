import json
import textwrap
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
print("\nGenerating structured answer...", flush=True)

answer_schema = {
    "type": "object",
    "properties": {
        "shared_indicators": {
            "type": "array",
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "indicator": {"type": "string"},
                    "india_ref": {
                        "type": "string",
                        "enum": ["E1", "E2"]
                    },
                    "us_ref": {
                        "type": "string",
                        "enum": ["E3", "E4"]
                    }
                },
                "required": [
                    "indicator",
                    "india_ref",
                    "us_ref"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": ["shared_indicators"],
    "additionalProperties": False
}

response = ollama.chat(
    model="qwen3:4b",
    think=False,
    stream=False,
    format=answer_schema,
    messages=[
        {
            "role": "system",
            "content": (
                "You are FinLLM. Return only the requested "
                "structured answer. Identify at most two "
                "suspicious transaction indicators supported "
                "by BOTH documents. Each indicator must have "
                "one supporting Indian evidence reference "
                "and one US evidence reference. "
                "Use only the supplied excerpts. "
                "If there is no supported overlap, "
                "return an empty list."
            )
        },
        {
            "role": "user",
            "content": (
                "/no_think\n"
                f"Question: {question}\n\n"
                f"Evidence:\n{evidence_text}"
            )
        }
    ],
    options={
        "num_ctx": 4096,
        "num_predict": 300,
        "temperature": 0
    }
)

print("\n========== FINLLM ANSWER ==========\n")

try:
    result = json.loads(
        response["message"]["content"]
    )

    indicators = result["shared_indicators"]

    if not indicators:
        print(
            "No common indicators are established "
            "by the retrieved evidence."
        )

    for item in indicators:
        print(item["indicator"])
        print(
            f"Sources: India [{item['india_ref']}], "
            f"US [{item['us_ref']}]\n"
        )

except (json.JSONDecodeError, KeyError) as error:
    print("Structured answer error:", error)
    print(response["message"]["content"])

print(
    "Generation stop reason:",
    response.get("done_reason", "unknown")
)

# ------------------------------------
# Show the retrieved evidence
# ------------------------------------

print("\n========== EVIDENCE SOURCES ==========\n")

for reference in evidence:
    print(reference)

print("\nTest finished.")