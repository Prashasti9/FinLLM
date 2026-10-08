
import chromadb
import ollama

# Connect to our completed chunk index
client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="finllm_policy_chunks_v1"
)

print(
    f"Connected: {collection.count()} chunks",
    flush=True
)

question = input("\nAsk FinLLM: ").strip()

if not question:
    raise SystemExit("Please enter a question.")

# Embed the question
print("\nEmbedding question...", flush=True)

embedding = ollama.embed(
    model="nomic-embed-text",
    input=question
)["embeddings"][0]

# Retrieve relevant evidence from BOTH PDFs
sources = [
    "kyc_policy.pdf",
    "msb_prevention_guide.pdf"
]

context = ""
retrieved_sources = []

for filename in sources:
    print(f"Searching {filename}...", flush=True)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=2,
        where={"source": filename}
    )

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        page = metadata["page"]
        jurisdiction = metadata["jurisdiction"]

        reference = f"{filename}, PDF page {page}"

        retrieved_sources.append(reference)

        context += (
            f"\nSOURCE: {filename}\n"
            f"PDF PAGE: {page}\n"
            f"JURISDICTION: {jurisdiction}\n"
            f"TEXT:\n{document}\n"
        )

        print(f"Found: {reference}", flush=True)

# Generate an evidence-based answer
print("\nGenerating answer...", flush=True)

messages = [
    {
        "role": "system",
        "content": (
            "You are FinLLM, a financial document assistant. "
            "Answer only from the supplied evidence. "
            "Distinguish US and Indian policies. "
            "For comparisons, explain what each document "
            "supports and identify genuinely common points. "
            "Cite the source filename and PDF page. "
            "If evidence is insufficient, say so. "
            "Do not treat older documents as current law. "
            "Keep the answer concise."
        )
    },
    {
        "role": "user",
        "content": (
            f"QUESTION:\n{question}\n\n"
            f"EVIDENCE:\n{context}"
        )
    }
]

stream = ollama.chat(
    model="qwen3:4b",
    messages=messages,
    think=False,
    stream=True,
    options={
        "num_ctx": 4096,
        "num_predict": 450
    }
)

print("\n========== FINLLM ANSWER ==========\n")

for chunk in stream:
    print(
        chunk["message"]["content"],
        end="",
        flush=True
    )

print("\n\n========== RETRIEVED SOURCES ==========")

for source in retrieved_sources:
    print(source)

print("\nTest finished.")