"""FinLLM v3: local, question-driven RAG over the existing ChromaDB index."""

import json
import re

import chromadb
import ollama


# 1. Connect to the EXISTING index; do not rebuild your 232 chunks.
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="finllm_policy_chunks_v1")
print(f"Connected: {collection.count()} chunks", flush=True)

question = input("\nAsk FinLLM: ").strip()
if not question:
    raise SystemExit("Please enter a question.")


# 2. Choose the document(s) named in the question.
q = question.lower()
asks_india = bool(re.search(r"\b(india|indian|kyc)\b", q))
asks_us = bool(re.search(r"\b(fincen|american|msb|msbs)\b|united states|u\.s\.", q))

if asks_india and not asks_us:
    sources = ["kyc_policy.pdf"]
elif asks_us and not asks_india:
    sources = ["msb_prevention_guide.pdf"]
else:
    sources = ["kyc_policy.pdf", "msb_prevention_guide.pdf"]

print("\nDocuments to search:")
for filename in sources:
    print(f"- {filename}")


# 3. Read indexed chunks, both for retrieval and for a basic unsupported-
#    company check. A 232-chunk local collection fits comfortably in memory.
indexed = collection.get(include=["documents", "metadatas"])
records = [
    (item_id, document, metadata)
    for item_id, document, metadata in zip(
        indexed["ids"], indexed["documents"], indexed["metadatas"]
    )
    if document and metadata and metadata.get("source") in sources
]

# Do not ask a compliance-policy PDF to invent financial statements for a
# company it never discusses. Other unsupported questions go to the LLM's
# evidence check below.
company_metric = re.search(
    r"\b([A-Z][A-Za-z0-9&.-]+)(?:['\u2019]s)?\s+"
    r"(revenue|profit|earnings|income|sales|assets)\b",
    question,
)
if company_metric:
    company, metric = company_metric.groups()
    year = re.search(r"\b(?:19|20)\d{2}\b", question)
    matching_chunks = [
        text for _, text, _ in records
        if company.casefold() in text.casefold()
        and metric.casefold() in text.casefold()
        and (year is None or year.group() in text)
    ]
    if not matching_chunks:
        print("\n========== FINLLM ANSWER ==========\n")
        print("The indexed documents do not contain enough evidence "
              "to answer this company's financial question.")
        print("\nNo supporting sources.\nTest finished.")
        raise SystemExit(0)


# 4. Embed the ACTUAL question, not a fixed fraud-related query.
print("\nEmbedding your question...", flush=True)
question_embedding = ollama.embed(
    model="nomic-embed-text", input=question
)["embeddings"][0]

stopwords = {
    "what", "does", "about", "which", "where", "when", "from",
    "with", "this", "that", "both", "their", "the", "and", "how",
    "indian", "india", "fincen", "united", "states", "policy",
    "guide", "document", "documents", "please", "explain", "say",
    "says", "tell", "there", "are", "was", "were",
}


def search_terms(text):
    terms = set()
    for word in re.findall(r"[a-z]{4,}", text.lower()):
        if word in stopwords:
            continue
        if len(word) > 6 and word.endswith("ing"):
            word = word[:-3]  # monitoring -> monitor
        elif len(word) > 5 and word.endswith("s") and not word.endswith(
            ("ss", "us")
        ):
            word = word[:-1]  # transactions -> transaction
        terms.add(word)
    return terms


terms = search_terms(question)
evidence = []
evidence_text = ""
evidence_map = {}
evidence_meta = {}
chunks_per_document = 3 if len(sources) == 1 else 2


# 5. Retrieve and rerank chunks for each relevant PDF.
for filename in sources:
    print(f"\nSearching: {filename}", flush=True)
    source_records = [
        record for record in records if record[2]["source"] == filename
    ]
    if not source_records:
        print("No indexed chunks for this PDF.")
        continue

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(12, len(source_records)),
        where={"source": filename},
        include=["documents", "metadatas", "distances"],
    )
    semantic_rank = {
        item_id: rank for rank, item_id in enumerate(results["ids"][0])
    }

    candidates = []
    for item_id, document, metadata in source_records:
        content = document.lower()
        keyword_coverage = sum(term in content for term in terms)
        rank = semantic_rank.get(item_id)
        semantic_bonus = 4 / (rank + 1) if rank is not None else 0
        score = keyword_coverage * 2 + semantic_bonus
        candidates.append((score, document, metadata))

    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = []
    used_pages = set()
    for candidate in candidates:
        page = candidate[2].get("page")
        if page in used_pages:
            continue
        selected.append(candidate)
        used_pages.add(page)
        if len(selected) == chunks_per_document:
            break

    for _, document, metadata in selected:
        label = f"E{len(evidence) + 1}"
        source = metadata["source"]
        page = metadata.get("page", "unknown")
        jurisdiction = metadata.get("jurisdiction", "unspecified")

        # Limit each excerpt to keep Qwen's context manageable. The quote
        # verifier checks against precisely this supplied excerpt.
        excerpt = document[:1250]
        evidence.append(f"[{label}] {source}, PDF page {page}")
        evidence_map[label] = excerpt
        evidence_meta[label] = {"source": source, "page": page}
        evidence_text += (
            f"\n[{label}] DOCUMENT: {source}; PDF PAGE: {page}; "
            f"JURISDICTION: {jurisdiction}\n{excerpt}\n"
        )
        print(f"Selected [{label}]: {source}, PDF page {page}", flush=True)

if not evidence:
    raise SystemExit("No evidence was retrieved. Check the PDF source names.")


# 6. Schema supports ANY document question, not just shared fraud indicators.
answer_schema = {
    "type": "object",
    "properties": {
        "supported": {"type": "boolean"},
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "enum": list(evidence_map)},
                    "quote": {"type": "string"},
                },
                "required": ["label", "quote"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["supported", "answer", "citations"],
    "additionalProperties": False,
}


# 7. Generate a short structured answer locally.
print("\nGenerating structured answer (this may take a minute)...", flush=True)
response = ollama.chat(
    model="qwen3:4b",
    think=False,
    stream=False,
    format=answer_schema,
    messages=[
        {
            "role": "system",
            "content": (
                "You are FinLLM. Answer the actual question using ONLY the "
                "provided excerpts. Do not force a comparison unless asked. "
                "If the excerpts do not answer the question, set supported "
                "to false and citations to []. If supported, answer in at "
                "most 90 words and provide 1-4 citations using evidence "
                "labels. Each citation quote MUST be a short, exact, "
                "consecutive excerpt from the specified evidence (no "
                "paraphrase or ellipsis). Do not invent facts. The policies "
                "may be historical; do not call them current law. "
                "Return only the JSON object."
            ),
        },
        {
            "role": "user",
            "content": (
                f"/no_think\nQUESTION: {question}\n\n"
                f"EVIDENCE:\n{evidence_text}\n"
                "Answer directly from the evidence."
            ),
        },
    ],
    options={"num_ctx": 4096, "num_predict": 500, "temperature": 0},
)


# 8. Refuse truncated or invalid output; verify quoted citations.
print("\n========== FINLLM ANSWER ==========\n")
stop_reason = response.get("done_reason", "unknown")
print("Generation stop reason:", stop_reason)
if stop_reason == "length":
    raise SystemExit("Output was truncated. Try a shorter question.")

try:
    result = json.loads(response["message"]["content"])
except (KeyError, ValueError, TypeError) as error:
    raise SystemExit(f"Invalid JSON answer: {error}")


def normalize(text):
    return " ".join(text.split()).casefold()


if not result.get("supported"):
    print("The provided documents do not contain enough evidence "
          "to answer this question.")
else:
    citations = result.get("citations", [])
    verified = []
    all_valid = bool(citations)
    for citation in citations:
        label = citation.get("label", "")
        quote = citation.get("quote", "").strip()
        original = evidence_map.get(label, "")
        if len(quote) >= 12 and normalize(quote) in normalize(original):
            verified.append((label, quote))
        else:
            all_valid = False
            print(f"Unverified quotation from [{label}].")

    # For a question explicitly about both documents, require at least one
    # verified citation from each. Exact quote matching is NOT a substitute
    # for human review of whether a passage supports the associated claim.
    cited_sources = {evidence_meta[label]["source"] for label, _ in verified}
    comparison_requested = (asks_india and asks_us) or bool(
        re.search(r"\b(both|compare|comparison|differences|similarities)\b", q)
    )
    if comparison_requested and len(sources) == 2 and len(cited_sources) < 2:
        all_valid = False

    if not all_valid:
        print("Answer withheld: citations are missing or unverified. "
              "Review the retrieved passages; do not use this as a "
              "compliance conclusion.")
    else:
        print(result.get("answer", ""))
        print("\nVerified quotations (review their relevance):")
        for label, quote in verified:
            metadata = evidence_meta[label]
            print(f"[{label}] {metadata['source']}, PDF page "
                  f"{metadata['page']}\n  \"{quote}\"")


# 9. Show source metadata even if answer was withheld.
print("\n========== RETRIEVED SOURCES ==========\n")
for reference in evidence:
    print(reference)
print("\nTest finished.")
